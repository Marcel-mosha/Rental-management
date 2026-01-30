from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone

from .models import Payment
from .serializers import (
    PaymentSerializer, PaymentListSerializer, PaymentCreateSerializer,
    PaymentVerificationSerializer
)
from .filters import PaymentFilter
from accounts.permissions import IsOwnerOrAdmin
from notifications.services import NotificationService


class PaymentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing payments."""
    
    queryset = Payment.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PaymentFilter
    search_fields = ['tenant__user__first_name', 'tenant__user__last_name',
                     'transaction_id', 'mobile_money_code', 'receipt_number']
    ordering_fields = ['payment_date', 'due_date', 'amount', 'created_at']
    ordering = ['-due_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PaymentListSerializer
        if self.action == 'create':
            return PaymentCreateSerializer
        return PaymentSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Payment.objects.all()
        
        queryset = Payment.objects.none()
        
        if hasattr(user, 'tenant_profile'):
            queryset = queryset | Payment.objects.filter(
                tenant=user.tenant_profile
            )
        
        if hasattr(user, 'owner_profile'):
            queryset = queryset | Payment.objects.filter(
                owner=user.owner_profile
            )
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        payment = serializer.save()
        
        # Send notification to owner
        NotificationService.send_payment_received(payment)
    
    @action(detail=True, methods=['post'], permission_classes=[IsOwnerOrAdmin])
    def verify(self, request, pk=None):
        """Verify a payment (manual verification)."""
        payment = self.get_object()
        serializer = PaymentVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        
        if action_type == 'approve':
            payment.payment_status = 'completed'
            payment.verified_by = request.user
            payment.verified_at = timezone.now()
            if not payment.payment_date:
                payment.payment_date = timezone.now().date()
            payment.generate_receipt_number()
            
            if serializer.validated_data.get('transaction_id'):
                payment.transaction_id = serializer.validated_data['transaction_id']
            
            # Update owner earnings
            owner = payment.owner
            owner.total_earnings += payment.amount
            owner.save(update_fields=['total_earnings'])
            
            # Send notification
            NotificationService.send_payment_verified(payment)
            
        else:  # reject
            payment.payment_status = 'failed'
            payment.notes = serializer.validated_data.get('notes', '')
            
            # Send notification
            NotificationService.send_payment_rejected(payment)
        
        payment.save()
        return Response(PaymentSerializer(payment).data)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get all pending payments."""
        payments = self.get_queryset().filter(payment_status='pending')
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def pending_verification(self, request):
        """Get payments pending verification."""
        payments = self.get_queryset().filter(
            payment_status='pending_verification'
        )
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get all overdue payments."""
        today = timezone.now().date()
        payments = self.get_queryset().filter(
            payment_status='pending',
            due_date__lt=today
        )
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
