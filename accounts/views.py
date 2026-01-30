from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta

from .models import Document, Tenant, Owner
from .serializers import (
    UserSerializer, UserListSerializer, UserRegistrationSerializer,
    ChangePasswordSerializer, DocumentSerializer,
    TenantSerializer, TenantListSerializer, TenantCreateSerializer,
    OwnerSerializer, OwnerListSerializer, OwnerCreateSerializer
)
from .dashboard import TenantDashboardSerializer, OwnerDashboardSerializer, AdminDashboardSerializer
from .permissions import IsOwner, IsTenant, IsOwnerOrAdmin, IsTenantOrAdmin
from notifications.services import NotificationService

User = get_user_model()


# ==================== User ViewSets ====================

class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users."""
    
    queryset = User.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering_fields = ['username', 'date_joined', 'user_type']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        if self.action == 'list':
            return UserListSerializer
        return UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]
        if self.action in ['list', 'verify_user']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update current authenticated user."""
        if request.method == 'GET':
            serializer = UserSerializer(request.user)
            return Response(serializer.data)
        
        serializer = UserSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if not request.user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'old_password': 'Incorrect password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'message': 'Password changed successfully'})
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def verify_user(self, request, pk=None):
        """Admin action to verify a user."""
        user = self.get_object()
        user.is_verified = True
        user.save()
        
        # Send notification
        NotificationService.send_account_verified(user)
        
        return Response({'message': f'User {user.username} verified successfully'})


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing documents."""
    
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def verify(self, request, pk=None):
        """Admin action to verify a document."""
        document = self.get_object()
        document.is_verified = True
        document.verification_notes = request.data.get('notes', '')
        document.save()
        
        # Send notification
        NotificationService.send_document_verified(document)
        
        return Response({'message': 'Document verified successfully'})


# ==================== Tenant ViewSet ====================

class TenantViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tenant profiles."""
    
    queryset = Tenant.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 
                     'user__phone_number', 'occupation']
    ordering_fields = ['created_at', 'user__last_name']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TenantListSerializer
        if self.action == 'create':
            return TenantCreateSerializer
        return TenantSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsTenantOrAdmin()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Tenant.objects.all()
        if hasattr(self.request.user, 'tenant_profile'):
            return Tenant.objects.filter(user=self.request.user)
        # Owners can see their tenants
        if hasattr(self.request.user, 'owner_profile'):
            from leases.models import LeaseAgreement
            owner = self.request.user.owner_profile
            tenant_ids = LeaseAgreement.objects.filter(
                unit__property__owner=owner
            ).values_list('tenant_id', flat=True)
            return Tenant.objects.filter(id__in=tenant_ids)
        return Tenant.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current user's tenant profile."""
        if not hasattr(request.user, 'tenant_profile'):
            return Response(
                {'error': 'Tenant profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TenantSerializer(request.user.tenant_profile)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def leases(self, request, pk=None):
        """Get all leases for a tenant."""
        from leases.serializers import LeaseListSerializer
        tenant = self.get_object()
        leases = tenant.leases.all()
        serializer = LeaseListSerializer(leases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all payments by a tenant."""
        from payments.serializers import PaymentListSerializer
        tenant = self.get_object()
        payments = tenant.payments.all()
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)


# ==================== Owner ViewSet ====================

class OwnerViewSet(viewsets.ModelViewSet):
    """ViewSet for managing owner profiles."""
    
    queryset = Owner.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user__first_name', 'user__last_name', 'user__email',
                     'user__phone_number', 'company_name']
    ordering_fields = ['created_at', 'total_properties']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return OwnerListSerializer
        if self.action == 'create':
            return OwnerCreateSerializer
        return OwnerSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsOwnerOrAdmin()]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Owner.objects.all()
        if hasattr(self.request.user, 'owner_profile'):
            return Owner.objects.filter(user=self.request.user)
        return Owner.objects.none()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_profile(self, request):
        """Get current user's owner profile."""
        if not hasattr(request.user, 'owner_profile'):
            return Response(
                {'error': 'Owner profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = OwnerSerializer(request.user.owner_profile)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def properties(self, request, pk=None):
        """Get all properties owned by this owner."""
        from properties.serializers import PropertyListSerializer
        owner = self.get_object()
        properties = owner.properties.all()
        serializer = PropertyListSerializer(
            properties, many=True, context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def earnings(self, request, pk=None):
        """Get earnings summary for an owner."""
        owner = self.get_object()
        
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        start_of_year = today.replace(month=1, day=1)
        
        payments = owner.received_payments.filter(payment_status='completed')
        
        monthly_earnings = payments.filter(
            payment_date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        yearly_earnings = payments.filter(
            payment_date__gte=start_of_year
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        total_earnings = payments.aggregate(total=Sum('amount'))['total'] or 0
        
        return Response({
            'monthly_earnings': monthly_earnings,
            'yearly_earnings': yearly_earnings,
            'total_earnings': total_earnings
        })


# ==================== Dashboard Views ====================

class TenantDashboardView(APIView):
    """Dashboard view for tenants."""
    
    permission_classes = [IsTenant]
    
    def get(self, request):
        tenant = request.user.tenant_profile
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Active leases
        active_leases = tenant.leases.filter(status='active').count()
        
        # Pending payments
        pending_payments = tenant.payments.filter(
            payment_status__in=['pending', 'pending_verification']
        ).count()
        
        # Total paid this month
        total_paid = tenant.payments.filter(
            payment_status='completed',
            payment_date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Upcoming due payments (next 7 days)
        seven_days = today + timedelta(days=7)
        upcoming = tenant.payments.filter(
            payment_status='pending',
            due_date__gte=today,
            due_date__lte=seven_days
        ).values('id', 'amount', 'due_date', 'payment_period')
        
        # Open maintenance requests
        open_maintenance = tenant.maintenance_requests.filter(
            status__in=['submitted', 'acknowledged', 'in_progress']
        ).count()
        
        # Unread notifications
        unread_notifications = request.user.notifications.filter(
            is_read=False
        ).count()
        
        data = {
            'active_leases': active_leases,
            'pending_payments': pending_payments,
            'total_paid_this_month': total_paid,
            'upcoming_due_payments': list(upcoming),
            'open_maintenance_requests': open_maintenance,
            'unread_notifications': unread_notifications
        }
        
        serializer = TenantDashboardSerializer(data)
        return Response(serializer.data)


class OwnerDashboardView(APIView):
    """Dashboard view for property owners."""
    
    permission_classes = [IsOwner]
    
    def get(self, request):
        from properties.models import RentalUnit
        from leases.models import LeaseAgreement
        
        owner = request.user.owner_profile
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        thirty_days = today + timedelta(days=30)
        
        # Properties and units
        properties = owner.properties.all()
        total_properties = properties.count()
        total_units = RentalUnit.objects.filter(property__owner=owner).count()
        occupied_units = RentalUnit.objects.filter(
            property__owner=owner, is_occupied=True
        ).count()
        
        vacancy_rate = 0
        if total_units > 0:
            vacancy_rate = ((total_units - occupied_units) / total_units) * 100
        
        # Leases
        active_leases = LeaseAgreement.objects.filter(
            unit__property__owner=owner, status='active'
        ).count()
        
        # Payments
        pending_payments = owner.received_payments.filter(
            payment_status__in=['pending', 'pending_verification']
        ).count()
        
        revenue_this_month = owner.received_payments.filter(
            payment_status='completed',
            payment_date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Maintenance
        pending_maintenance = owner.maintenance_requests.filter(
            status__in=['submitted', 'acknowledged', 'in_progress']
        ).count()
        
        # Recent payments (last 5)
        recent_payments = owner.received_payments.filter(
            payment_status='completed'
        ).order_by('-payment_date')[:5].values(
            'id', 'amount', 'payment_date', 'payment_period'
        )
        
        # Expiring leases
        expiring_leases = LeaseAgreement.objects.filter(
            unit__property__owner=owner,
            status='active',
            end_date__gte=today,
            end_date__lte=thirty_days
        ).values('id', 'tenant__user__first_name', 'end_date')
        
        # Unread notifications
        unread_notifications = request.user.notifications.filter(
            is_read=False
        ).count()
        
        data = {
            'total_properties': total_properties,
            'total_units': total_units,
            'occupied_units': occupied_units,
            'vacancy_rate': round(vacancy_rate, 2),
            'active_leases': active_leases,
            'pending_payments': pending_payments,
            'revenue_this_month': revenue_this_month,
            'pending_maintenance': pending_maintenance,
            'recent_payments': list(recent_payments),
            'expiring_leases': list(expiring_leases),
            'unread_notifications': unread_notifications
        }
        
        serializer = OwnerDashboardSerializer(data)
        return Response(serializer.data)


class AdminDashboardView(APIView):
    """Dashboard view for administrators."""
    
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        from properties.models import Property, RentalUnit
        from leases.models import LeaseAgreement
        from payments.models import Payment
        
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Users
        total_users = User.objects.count()
        total_tenants = Tenant.objects.count()
        total_owners = Owner.objects.count()
        
        # Properties
        total_properties = Property.objects.count()
        total_units = RentalUnit.objects.count()
        
        # Leases
        active_leases = LeaseAgreement.objects.filter(status='active').count()
        
        # Verifications
        pending_verifications = User.objects.filter(is_verified=False).count()
        
        # Payments
        payments_this_month = Payment.objects.filter(
            payment_status='completed',
            payment_date__gte=start_of_month
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        pending_payment_verifications = Payment.objects.filter(
            payment_status='pending_verification'
        ).count()
        
        data = {
            'total_users': total_users,
            'total_tenants': total_tenants,
            'total_owners': total_owners,
            'total_properties': total_properties,
            'total_units': total_units,
            'active_leases': active_leases,
            'pending_verifications': pending_verifications,
            'payments_this_month': payments_this_month,
            'pending_payment_verifications': pending_payment_verifications
        }
        
        serializer = AdminDashboardSerializer(data)
        return Response(serializer.data)
