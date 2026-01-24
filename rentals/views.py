from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta

from .models import (
    Document, Tenant, Owner, Location, Property, PropertyImage,
    PropertyAmenity, RentalUnit, LeaseAgreement, Payment,
    MaintenanceRequest, MaintenanceImage, Review, Notification
)
from .serializers import (
    UserSerializer, UserListSerializer, UserRegistrationSerializer,
    ChangePasswordSerializer, DocumentSerializer,
    TenantSerializer, TenantListSerializer, TenantCreateSerializer,
    OwnerSerializer, OwnerListSerializer, OwnerCreateSerializer,
    LocationSerializer,
    PropertySerializer, PropertyListSerializer, PropertyCreateSerializer,
    PropertyImageSerializer, PropertyAmenitySerializer,
    RentalUnitSerializer, RentalUnitListSerializer,
    LeaseSerializer, LeaseListSerializer, LeaseRenewalSerializer,
    PaymentSerializer, PaymentListSerializer, PaymentCreateSerializer,
    PaymentVerificationSerializer,
    MaintenanceRequestSerializer, MaintenanceRequestListSerializer,
    MaintenanceRequestCreateSerializer, MaintenanceStatusUpdateSerializer,
    MaintenanceImageSerializer,
    ReviewSerializer, ReviewListSerializer, ReviewCreateSerializer,
    ReviewResponseSerializer,
    NotificationSerializer,
    TenantDashboardSerializer, OwnerDashboardSerializer, AdminDashboardSerializer
)
from .filters import (
    PropertyFilter, RentalUnitFilter, LeaseFilter, 
    PaymentFilter, MaintenanceRequestFilter
)
from .permissions import (
    IsOwner, IsTenant, IsOwnerOrAdmin, IsTenantOrAdmin, 
    IsPropertyOwner, IsLeaseParticipant
)
from .services import NotificationService

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
        tenant = self.get_object()
        leases = tenant.leases.all()
        serializer = LeaseListSerializer(leases, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all payments by a tenant."""
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


# ==================== Property ViewSet ====================

class PropertyViewSet(viewsets.ModelViewSet):
    """ViewSet for managing properties."""
    
    queryset = Property.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PropertyFilter
    search_fields = ['title', 'description', 'location__district', 
                     'location__ward', 'location__street_address']
    ordering_fields = ['monthly_rent', 'listed_date', 'created_at']
    ordering = ['-listed_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        if self.action == 'create':
            return PropertyCreateSerializer
        return PropertySerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        if self.action == 'create':
            return [IsOwner()]
        return [IsPropertyOwner()]
    
    def get_queryset(self):
        queryset = Property.objects.select_related('owner', 'location')
        
        # Filter by owner if specified
        owner_only = self.request.query_params.get('my_properties')
        if owner_only and hasattr(self.request.user, 'owner_profile'):
            queryset = queryset.filter(owner=self.request.user.owner_profile)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available properties."""
        properties = Property.objects.filter(is_available=True)
        serializer = PropertyListSerializer(
            properties, many=True, context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def units(self, request, pk=None):
        """Get all units for a property."""
        property_obj = self.get_object()
        units = property_obj.units.all()
        serializer = RentalUnitSerializer(units, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a property."""
        property_obj = self.get_object()
        reviews = property_obj.reviews.filter(is_visible=True)
        serializer = ReviewListSerializer(reviews, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def add_image(self, request, pk=None):
        """Add an image to a property."""
        property_obj = self.get_object()
        serializer = PropertyImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(property=property_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def add_amenities(self, request, pk=None):
        """Add amenities to a property."""
        property_obj = self.get_object()
        amenities = request.data.get('amenities', [])
        
        created = []
        for amenity_code in amenities:
            amenity, is_created = PropertyAmenity.objects.get_or_create(
                property=property_obj,
                amenity=amenity_code
            )
            if is_created:
                created.append(amenity_code)
        
        return Response({
            'message': f'Added {len(created)} amenities',
            'amenities': created
        })


class PropertyImageViewSet(viewsets.ModelViewSet):
    """ViewSet for property images."""
    
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        property_id = self.request.query_params.get('property')
        if property_id:
            return PropertyImage.objects.filter(property_id=property_id)
        return PropertyImage.objects.all()


# ==================== Rental Unit ViewSet ====================

class RentalUnitViewSet(viewsets.ModelViewSet):
    """ViewSet for managing rental units."""
    
    queryset = RentalUnit.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = RentalUnitFilter
    search_fields = ['unit_number', 'property__title']
    ordering_fields = ['unit_rent', 'created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RentalUnitListSerializer
        return RentalUnitSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsPropertyOwner()]
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available (unoccupied) units."""
        units = RentalUnit.objects.filter(is_occupied=False)
        serializer = RentalUnitListSerializer(units, many=True)
        return Response(serializer.data)


# ==================== Lease ViewSet ====================

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
        lease = self.get_object()
        payments = lease.payments.all()
        serializer = PaymentListSerializer(payments, many=True)
        return Response(serializer.data)


# ==================== Payment ViewSet ====================

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


# ==================== Maintenance Request ViewSet ====================

class MaintenanceRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for managing maintenance requests."""
    
    queryset = MaintenanceRequest.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MaintenanceRequestFilter
    search_fields = ['description', 'unit__property__title', 'technician_name']
    ordering_fields = ['priority', 'status', 'request_date']
    ordering = ['-request_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MaintenanceRequestListSerializer
        if self.action == 'create':
            return MaintenanceRequestCreateSerializer
        return MaintenanceRequestSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return MaintenanceRequest.objects.all()
        
        queryset = MaintenanceRequest.objects.none()
        
        if hasattr(user, 'tenant_profile'):
            queryset = queryset | MaintenanceRequest.objects.filter(
                tenant=user.tenant_profile
            )
        
        if hasattr(user, 'owner_profile'):
            queryset = queryset | MaintenanceRequest.objects.filter(
                owner=user.owner_profile
            )
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        request = serializer.save()
        
        # Send notification to owner
        NotificationService.send_maintenance_submitted(request)
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update maintenance request status."""
        maintenance_request = self.get_object()
        serializer = MaintenanceStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        old_status = maintenance_request.status
        new_status = serializer.validated_data['status']
        
        maintenance_request.status = new_status
        
        if new_status == 'acknowledged' and old_status == 'submitted':
            maintenance_request.acknowledged_date = timezone.now()
        
        if new_status == 'completed':
            maintenance_request.resolved_date = timezone.now()
            if 'cost' in serializer.validated_data:
                maintenance_request.cost = serializer.validated_data['cost']
            if 'cost_responsibility' in serializer.validated_data:
                maintenance_request.cost_responsibility = serializer.validated_data['cost_responsibility']
        
        if 'resolution_notes' in serializer.validated_data:
            maintenance_request.resolution_notes = serializer.validated_data['resolution_notes']
        if 'technician_name' in serializer.validated_data:
            maintenance_request.technician_name = serializer.validated_data['technician_name']
        if 'technician_contact' in serializer.validated_data:
            maintenance_request.technician_contact = serializer.validated_data['technician_contact']
        
        maintenance_request.save()
        
        # Send notification based on status change
        NotificationService.send_maintenance_update(maintenance_request, new_status)
        
        return Response(MaintenanceRequestSerializer(maintenance_request).data)
    
    @action(detail=True, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def add_image(self, request, pk=None):
        """Add an image to a maintenance request."""
        maintenance_request = self.get_object()
        serializer = MaintenanceImageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(maintenance_request=maintenance_request)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get urgent and high priority pending requests."""
        requests = self.get_queryset().filter(
            priority__in=['urgent', 'high'],
            status__in=['submitted', 'acknowledged', 'in_progress']
        )
        serializer = MaintenanceRequestListSerializer(requests, many=True)
        return Response(serializer.data)


# ==================== Review ViewSet ====================

class ReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for managing reviews."""
    
    queryset = Review.objects.all()
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['rating', 'review_date']
    ordering = ['-review_date']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ReviewListSerializer
        if self.action == 'create':
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def get_permissions(self):
        return [IsAuthenticated()]
    
    def get_queryset(self):
        queryset = Review.objects.filter(is_visible=True)
        
        # Filter by property if specified
        property_id = self.request.query_params.get('property')
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        
        # Filter by tenant if specified
        tenant_id = self.request.query_params.get('tenant')
        if tenant_id:
            queryset = queryset.filter(tenant_id=tenant_id)
        
        return queryset
    
    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        """Add a response to a review."""
        review = self.get_object()
        serializer = ReviewResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify the responder is authorized
        user = request.user
        can_respond = False
        
        if review.review_type == 'tenant_to_property':
            # Owner can respond
            if hasattr(user, 'owner_profile') and review.property.owner == user.owner_profile:
                can_respond = True
        elif review.review_type == 'owner_to_tenant':
            # Tenant can respond
            if hasattr(user, 'tenant_profile') and review.tenant == user.tenant_profile:
                can_respond = True
        
        if not can_respond:
            return Response(
                {'error': 'You are not authorized to respond to this review'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        review.response = serializer.validated_data['response']
        review.response_date = timezone.now()
        review.response_by = user
        review.save()
        
        # Send notification
        NotificationService.send_review_response(review)
        
        return Response(ReviewSerializer(review).data)


# ==================== Notification ViewSet ====================

class NotificationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notifications."""
    
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering = ['-created_at']
    http_method_names = ['get', 'patch', 'delete']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications."""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = NotificationSerializer(
            notifications, many=True, context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get count of unread notifications."""
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark a notification as read."""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read."""
        self.get_queryset().filter(is_read=False).update(is_read=True)
        return Response({'message': 'All notifications marked as read'})


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
