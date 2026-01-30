from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from datetime import timedelta

from .models import LeaseAgreement
from .serializers import LeaseSerializer, LeaseListSerializer, LeaseRenewalSerializer
from .filters import LeaseFilter
from accounts.permissions import IsLeaseParticipant
from notifications.services import NotificationService


class LeaseViewSet(viewsets.ModelViewSet):
    """ViewSet for managing lease agreements."""
    
    queryset = LeaseAgreement.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = LeaseFilter
    search_fields = ['tenant__user__first_name', 'tenant__user__last_name',
                     'unit__property__title']
    ordering_fields = ['start_date', 'end_date', 'monthly_rent', 'created_at']
    ordering = ['-start_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return LeaseListSerializer
        return LeaseSerializer
    
    def get_permissions(self):
        return [IsLeaseParticipant()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return LeaseAgreement.objects.all()
        
        queryset = LeaseAgreement.objects.none()
        
        if hasattr(user, 'tenant_profile'):
            queryset = queryset | LeaseAgreement.objects.filter(
                tenant=user.tenant_profile
            )
        
        if hasattr(user, 'owner_profile'):
            queryset = queryset | LeaseAgreement.objects.filter(
                unit__property__owner=user.owner_profile
            )
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        lease = serializer.save()
        
        # Update unit status
        lease.unit.is_occupied = True
        lease.unit.save()
        
        # Update property available rooms
        property_obj = lease.unit.property
        property_obj.available_rooms = property_obj.units.filter(
            is_occupied=False
        ).count()
        property_obj.save()
        
        # Send notification
        NotificationService.send_lease_created(lease)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a pending lease."""
        lease = self.get_object()
        if lease.status != 'pending':
            return Response(
                {'error': 'Only pending leases can be activated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        lease.status = 'active'
        lease.signed_date = timezone.now().date()
        lease.save()
        
        serializer = LeaseSerializer(lease)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def terminate(self, request, pk=None):
        """Terminate a lease early."""
        lease = self.get_object()
        lease.status = 'terminated'
        lease.save()
        
        # Free up the unit
        lease.unit.is_occupied = False
        lease.unit.save()
        
        return Response({'message': 'Lease terminated successfully'})
    
    @action(detail=True, methods=['post'])
    def renew(self, request, pk=None):
        """Renew an expiring/expired lease."""
        lease = self.get_object()
        serializer = LeaseRenewalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Mark old lease as renewed
        lease.status = 'renewed'
        lease.save()
        
        # Create new lease
        new_lease = LeaseAgreement.objects.create(
            tenant=lease.tenant,
            unit=lease.unit,
            start_date=serializer.validated_data['new_start_date'],
            end_date=serializer.validated_data['new_end_date'],
            monthly_rent=serializer.validated_data.get(
                'new_monthly_rent', lease.monthly_rent
            ),
            security_deposit=lease.security_deposit,
            deposit_paid=lease.deposit_paid,
            payment_frequency=lease.payment_frequency,
            payment_due_day=lease.payment_due_day,
            terms_conditions=lease.terms_conditions,
            status='active',
            signed_date=timezone.now().date()
        )
        
        # Send notification
        NotificationService.send_lease_renewed(new_lease)
        
        return Response(
            LeaseSerializer(new_lease).data, 
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get leases expiring within 30 days."""
        today = timezone.now().date()
        thirty_days = today + timedelta(days=30)
        
        leases = self.get_queryset().filter(
            status='active',
            end_date__gte=today,
            end_date__lte=thirty_days
        )
        serializer = LeaseListSerializer(leases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all payments for a lease."""
        from payments.serializers import PaymentListSerializer
        lease = self.get_object()
        payments = lease.payments.all()
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)
