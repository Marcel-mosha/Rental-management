from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import (
    Document, Tenant, Owner, Location, Property, PropertyImage,
    PropertyAmenity, RentalUnit, LeaseAgreement, Payment,
    MaintenanceRequest, MaintenanceImage, Review, Notification
)

User = get_user_model()


# ==================== User Serializers ====================

class UserListSerializer(serializers.ModelSerializer):
    """Minimal user data for listings."""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'full_name', 'email', 'phone_number', 
                  'user_type', 'is_verified']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserSerializer(serializers.ModelSerializer):
    """Full user details."""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'full_name', 'phone_number', 'user_type', 'profile_image',
                  'is_verified', 'preferred_language', 'registration_date']
        read_only_fields = ['id', 'registration_date', 'is_verified']
    
    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password_confirm',
                  'first_name', 'last_name', 'phone_number', 'user_type',
                  'preferred_language']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Passwords do not match.'
            })
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change."""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        return attrs


# ==================== Document Serializers ====================

class DocumentSerializer(serializers.ModelSerializer):
    """Document serializer."""
    document_type_display = serializers.CharField(
        source='get_document_type_display', read_only=True
    )
    
    class Meta:
        model = Document
        fields = ['id', 'user', 'document_type', 'document_type_display',
                  'document_file', 'upload_date', 'is_verified', 'verification_notes']
        read_only_fields = ['id', 'upload_date', 'is_verified', 'verification_notes']


# ==================== Tenant Serializers ====================

class TenantListSerializer(serializers.ModelSerializer):
    """Minimal tenant data for listings."""
    user = UserListSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = ['id', 'user', 'full_name', 'occupation']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()


class TenantSerializer(serializers.ModelSerializer):
    """Full tenant details."""
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    active_leases_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tenant
        fields = ['id', 'user', 'full_name', 'occupation', 'employer_name',
                  'monthly_income', 'emergency_contact_name', 'emergency_contact_phone',
                  'reference_name', 'reference_contact', 'active_leases_count',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    
    def get_active_leases_count(self, obj):
        return obj.leases.filter(status='active').count()


class TenantCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tenant profile."""
    
    class Meta:
        model = Tenant
        fields = ['occupation', 'employer_name', 'monthly_income',
                  'emergency_contact_name', 'emergency_contact_phone',
                  'reference_name', 'reference_contact']


# ==================== Owner Serializers ====================

class OwnerListSerializer(serializers.ModelSerializer):
    """Minimal owner data for listings."""
    user = UserListSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Owner
        fields = ['id', 'user', 'full_name', 'company_name', 'total_properties']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()


class OwnerSerializer(serializers.ModelSerializer):
    """Full owner details."""
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    bank_name_display = serializers.CharField(
        source='get_bank_name_display', read_only=True
    )
    
    class Meta:
        model = Owner
        fields = ['id', 'user', 'full_name', 'company_name', 
                  'tax_identification_number', 'bank_name', 'bank_name_display',
                  'account_number', 'account_name', 'total_properties',
                  'total_earnings', 'created_at', 'updated_at']
        read_only_fields = ['id', 'total_properties', 'total_earnings', 
                           'created_at', 'updated_at']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()


class OwnerCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating owner profile."""
    
    class Meta:
        model = Owner
        fields = ['company_name', 'tax_identification_number', 
                  'bank_name', 'account_number', 'account_name']


# ==================== Location Serializers ====================

class LocationSerializer(serializers.ModelSerializer):
    """Location serializer."""
    region_display = serializers.CharField(source='get_region_display', read_only=True)
    full_address = serializers.SerializerMethodField()
    
    class Meta:
        model = Location
        fields = ['id', 'region', 'region_display', 'district', 'ward', 
                  'street_address', 'latitude', 'longitude', 'landmark',
                  'full_address']
    
    def get_full_address(self, obj):
        return str(obj)


# ==================== Property Serializers ====================

class PropertyImageSerializer(serializers.ModelSerializer):
    """Property image serializer."""
    
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'caption', 'is_primary', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class PropertyAmenitySerializer(serializers.ModelSerializer):
    """Property amenity serializer."""
    amenity_display = serializers.CharField(source='get_amenity_display', read_only=True)
    
    class Meta:
        model = PropertyAmenity
        fields = ['id', 'amenity', 'amenity_display']


class RentalUnitListSerializer(serializers.ModelSerializer):
    """Minimal rental unit data."""
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    
    class Meta:
        model = RentalUnit
        fields = ['id', 'unit_number', 'unit_type', 'unit_type_display',
                  'unit_rent', 'is_occupied']


class RentalUnitSerializer(serializers.ModelSerializer):
    """Full rental unit details."""
    unit_type_display = serializers.CharField(source='get_unit_type_display', read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    current_lease = serializers.SerializerMethodField()
    
    class Meta:
        model = RentalUnit
        fields = ['id', 'property', 'property_title', 'unit_type', 
                  'unit_type_display', 'unit_number', 'unit_rent', 'area_sqm',
                  'is_occupied', 'unit_features', 'current_lease',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_current_lease(self, obj):
        active_lease = obj.leases.filter(status='active').first()
        if active_lease:
            return {
                'id': active_lease.id,
                'tenant_name': active_lease.tenant.user.get_full_name(),
                'start_date': active_lease.start_date,
                'end_date': active_lease.end_date
            }
        return None


class PropertyListSerializer(serializers.ModelSerializer):
    """Minimal property data for listings."""
    owner_name = serializers.SerializerMethodField()
    location_summary = serializers.SerializerMethodField()
    property_type_display = serializers.CharField(
        source='get_property_type_display', read_only=True
    )
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'title', 'property_type', 'property_type_display',
                  'monthly_rent', 'location_summary', 'owner_name',
                  'available_rooms', 'total_rooms', 'is_available',
                  'average_rating', 'primary_image', 'listed_date']
    
    def get_owner_name(self, obj):
        return obj.owner.user.get_full_name()
    
    def get_location_summary(self, obj):
        return f"{obj.location.ward}, {obj.location.district}"
    
    def get_primary_image(self, obj):
        primary = obj.images.filter(is_primary=True).first()
        if primary:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None


class PropertySerializer(serializers.ModelSerializer):
    """Full property details."""
    owner = OwnerListSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=Owner.objects.all(), source='owner', write_only=True
    )
    location = LocationSerializer()
    property_type_display = serializers.CharField(
        source='get_property_type_display', read_only=True
    )
    images = PropertyImageSerializer(many=True, read_only=True)
    amenities = PropertyAmenitySerializer(many=True, read_only=True)
    units = RentalUnitListSerializer(many=True, read_only=True)
    reviews_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'owner', 'owner_id', 'property_type', 'property_type_display',
                  'title', 'description', 'monthly_rent', 'location',
                  'total_rooms', 'available_rooms', 'is_available', 'listed_date',
                  'rules_terms', 'images', 'amenities', 'units', 'average_rating',
                  'reviews_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'listed_date', 'created_at', 'updated_at']
    
    def get_reviews_count(self, obj):
        return obj.reviews.filter(is_visible=True).count()
    
    def create(self, validated_data):
        location_data = validated_data.pop('location')
        location = Location.objects.create(**location_data)
        property_obj = Property.objects.create(location=location, **validated_data)
        return property_obj
    
    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        if location_data:
            for attr, value in location_data.items():
                setattr(instance.location, attr, value)
            instance.location.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PropertyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating properties."""
    location = LocationSerializer()
    amenities = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    
    class Meta:
        model = Property
        fields = ['property_type', 'title', 'description', 'monthly_rent',
                  'location', 'total_rooms', 'available_rooms', 'rules_terms',
                  'amenities']
    
    def create(self, validated_data):
        location_data = validated_data.pop('location')
        amenities_data = validated_data.pop('amenities', [])
        
        location = Location.objects.create(**location_data)
        
        # Get owner from context (current user)
        owner = self.context['request'].user.owner_profile
        property_obj = Property.objects.create(
            owner=owner, 
            location=location, 
            **validated_data
        )
        
        # Create amenities
        for amenity_code in amenities_data:
            PropertyAmenity.objects.create(property=property_obj, amenity=amenity_code)
        
        return property_obj


# ==================== Lease Serializers ====================

class LeaseListSerializer(serializers.ModelSerializer):
    """Minimal lease data for listings."""
    tenant_name = serializers.SerializerMethodField()
    unit_info = serializers.SerializerMethodField()
    property_title = serializers.CharField(source='unit.property.title', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = LeaseAgreement
        fields = ['id', 'tenant_name', 'property_title', 'unit_info',
                  'start_date', 'end_date', 'monthly_rent', 'status',
                  'status_display', 'is_active']
    
    def get_tenant_name(self, obj):
        return obj.tenant.user.get_full_name()
    
    def get_unit_info(self, obj):
        return f"Unit {obj.unit.unit_number}"


class LeaseSerializer(serializers.ModelSerializer):
    """Full lease details."""
    tenant = TenantListSerializer(read_only=True)
    tenant_id = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(), source='tenant', write_only=True
    )
    unit = RentalUnitSerializer(read_only=True)
    unit_id = serializers.PrimaryKeyRelatedField(
        queryset=RentalUnit.objects.all(), source='unit', write_only=True
    )
    property_info = serializers.SerializerMethodField()
    owner_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_frequency_display = serializers.CharField(
        source='get_payment_frequency_display', read_only=True
    )
    total_paid = serializers.SerializerMethodField()
    
    class Meta:
        model = LeaseAgreement
        fields = ['id', 'tenant', 'tenant_id', 'unit', 'unit_id',
                  'property_info', 'owner_info', 'start_date', 'end_date',
                  'monthly_rent', 'security_deposit', 'payment_frequency',
                  'payment_frequency_display', 'payment_due_day', 
                  'terms_conditions', 'agreement_document', 'status',
                  'status_display', 'signed_date', 'deposit_paid',
                  'deposit_paid_date', 'is_active', 'total_paid',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_property_info(self, obj):
        return {
            'id': obj.unit.property.id,
            'title': obj.unit.property.title,
            'address': str(obj.unit.property.location)
        }
    
    def get_owner_info(self, obj):
        owner = obj.unit.property.owner
        return {
            'id': owner.id,
            'name': owner.user.get_full_name(),
            'phone': owner.user.phone_number
        }
    
    def get_total_paid(self, obj):
        return sum(
            p.amount for p in obj.payments.filter(payment_status='completed')
        )
    
    def validate(self, attrs):
        if attrs.get('start_date') and attrs.get('end_date'):
            if attrs['start_date'] >= attrs['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date.'
                })
        return attrs


class LeaseRenewalSerializer(serializers.Serializer):
    """Serializer for lease renewal."""
    new_start_date = serializers.DateField()
    new_end_date = serializers.DateField()
    new_monthly_rent = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )
    
    def validate(self, attrs):
        if attrs['new_start_date'] >= attrs['new_end_date']:
            raise serializers.ValidationError({
                'new_end_date': 'End date must be after start date.'
            })
        return attrs


# ==================== Payment Serializers ====================

class PaymentListSerializer(serializers.ModelSerializer):
    """Minimal payment data for listings."""
    tenant_name = serializers.SerializerMethodField()
    property_title = serializers.CharField(
        source='lease.unit.property.title', read_only=True
    )
    status_display = serializers.CharField(
        source='get_payment_status_display', read_only=True
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display', read_only=True
    )
    
    class Meta:
        model = Payment
        fields = ['id', 'tenant_name', 'property_title', 'amount',
                  'payment_method', 'payment_method_display', 'payment_date',
                  'due_date', 'payment_period', 'payment_status', 'status_display',
                  'is_late']
    
    def get_tenant_name(self, obj):
        return obj.tenant.user.get_full_name()


class PaymentSerializer(serializers.ModelSerializer):
    """Full payment details."""
    tenant = TenantListSerializer(read_only=True)
    owner = OwnerListSerializer(read_only=True)
    lease_info = serializers.SerializerMethodField()
    status_display = serializers.CharField(
        source='get_payment_status_display', read_only=True
    )
    payment_method_display = serializers.CharField(
        source='get_payment_method_display', read_only=True
    )
    verified_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Payment
        fields = ['id', 'lease', 'lease_info', 'tenant', 'owner', 'amount',
                  'payment_date', 'payment_method', 'payment_method_display',
                  'transaction_id', 'payment_status', 'status_display',
                  'mobile_money_code', 'due_date', 'payment_period',
                  'receipt_number', 'receipt_file', 'notes', 'is_late',
                  'verified_by', 'verified_by_name', 'verified_at',
                  'created_at', 'updated_at']
        read_only_fields = ['id', 'receipt_number', 'verified_by', 
                           'verified_at', 'created_at', 'updated_at']
    
    def get_lease_info(self, obj):
        return {
            'id': obj.lease.id,
            'property_title': obj.lease.unit.property.title,
            'unit_number': obj.lease.unit.unit_number
        }
    
    def get_verified_by_name(self, obj):
        if obj.verified_by:
            return obj.verified_by.get_full_name()
        return None


class PaymentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/submitting payments."""
    
    class Meta:
        model = Payment
        fields = ['lease', 'amount', 'payment_method', 'payment_date',
                  'mobile_money_code', 'due_date', 'payment_period', 'notes']
    
    def create(self, validated_data):
        lease = validated_data['lease']
        validated_data['tenant'] = lease.tenant
        validated_data['owner'] = lease.unit.property.owner
        validated_data['payment_status'] = 'pending_verification'
        
        payment = Payment.objects.create(**validated_data)
        return payment


class PaymentVerificationSerializer(serializers.Serializer):
    """Serializer for verifying payments."""
    action = serializers.ChoiceField(choices=['approve', 'reject'])
    notes = serializers.CharField(required=False, allow_blank=True)
    transaction_id = serializers.CharField(required=False, allow_blank=True)


# ==================== Maintenance Request Serializers ====================

class MaintenanceImageSerializer(serializers.ModelSerializer):
    """Maintenance image serializer."""
    
    class Meta:
        model = MaintenanceImage
        fields = ['id', 'image', 'caption', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class MaintenanceRequestListSerializer(serializers.ModelSerializer):
    """Minimal maintenance request data."""
    tenant_name = serializers.SerializerMethodField()
    unit_info = serializers.SerializerMethodField()
    property_title = serializers.CharField(
        source='unit.property.title', read_only=True
    )
    issue_type_display = serializers.CharField(
        source='get_issue_type_display', read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = MaintenanceRequest
        fields = ['id', 'tenant_name', 'property_title', 'unit_info',
                  'issue_type', 'issue_type_display', 'priority',
                  'priority_display', 'status', 'status_display',
                  'request_date']
    
    def get_tenant_name(self, obj):
        return obj.tenant.user.get_full_name()
    
    def get_unit_info(self, obj):
        return f"Unit {obj.unit.unit_number}"


class MaintenanceRequestSerializer(serializers.ModelSerializer):
    """Full maintenance request details."""
    tenant = TenantListSerializer(read_only=True)
    owner = OwnerListSerializer(read_only=True)
    unit = RentalUnitListSerializer(read_only=True)
    images = MaintenanceImageSerializer(many=True, read_only=True)
    issue_type_display = serializers.CharField(
        source='get_issue_type_display', read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display', read_only=True
    )
    status_display = serializers.CharField(
        source='get_status_display', read_only=True
    )
    
    class Meta:
        model = MaintenanceRequest
        fields = ['id', 'tenant', 'unit', 'owner', 'issue_type',
                  'issue_type_display', 'description', 'priority',
                  'priority_display', 'status', 'status_display',
                  'request_date', 'acknowledged_date', 'resolved_date',
                  'cost', 'cost_responsibility', 'technician_name',
                  'technician_contact', 'resolution_notes', 'images']
        read_only_fields = ['id', 'request_date']


class MaintenanceRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating maintenance requests."""
    
    class Meta:
        model = MaintenanceRequest
        fields = ['unit', 'issue_type', 'description', 'priority']
    
    def create(self, validated_data):
        unit = validated_data['unit']
        
        # Get tenant from active lease
        active_lease = unit.leases.filter(status='active').first()
        if not active_lease:
            raise serializers.ValidationError({
                'unit': 'No active lease found for this unit.'
            })
        
        validated_data['tenant'] = active_lease.tenant
        validated_data['owner'] = unit.property.owner
        
        return MaintenanceRequest.objects.create(**validated_data)


class MaintenanceStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating maintenance status."""
    status = serializers.ChoiceField(
        choices=MaintenanceRequest.STATUS_CHOICES
    )
    resolution_notes = serializers.CharField(required=False, allow_blank=True)
    cost = serializers.DecimalField(
        max_digits=12, decimal_places=2, required=False
    )
    cost_responsibility = serializers.ChoiceField(
        choices=[('tenant', 'Tenant'), ('owner', 'Owner'), ('shared', 'Shared')],
        required=False
    )
    technician_name = serializers.CharField(required=False, allow_blank=True)
    technician_contact = serializers.CharField(required=False, allow_blank=True)


# ==================== Review Serializers ====================

class ReviewListSerializer(serializers.ModelSerializer):
    """Minimal review data."""
    reviewer_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'review_type', 'reviewer_name', 'rating', 
                  'comment', 'review_date', 'response', 'response_date']
    
    def get_reviewer_name(self, obj):
        return obj.reviewer.get_full_name()


class ReviewSerializer(serializers.ModelSerializer):
    """Full review details."""
    reviewer = UserListSerializer(read_only=True)
    property_info = serializers.SerializerMethodField()
    tenant_info = serializers.SerializerMethodField()
    response_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'review_type', 'reviewer', 'tenant_info', 
                  'property_info', 'lease', 'rating', 'comment', 
                  'review_date', 'response', 'response_date', 
                  'response_by', 'response_by_name', 'is_visible']
        read_only_fields = ['id', 'review_date', 'response_date', 'response_by']
    
    def get_property_info(self, obj):
        if obj.property:
            return {'id': obj.property.id, 'title': obj.property.title}
        return None
    
    def get_tenant_info(self, obj):
        if obj.tenant:
            return {'id': obj.tenant.id, 'name': obj.tenant.user.get_full_name()}
        return None
    
    def get_response_by_name(self, obj):
        if obj.response_by:
            return obj.response_by.get_full_name()
        return None


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews."""
    
    class Meta:
        model = Review
        fields = ['review_type', 'lease', 'rating', 'comment', 
                  'property', 'tenant']
    
    def validate(self, attrs):
        review_type = attrs.get('review_type')
        lease = attrs.get('lease')
        
        # Verify the lease exists and reviewer has access
        request = self.context.get('request')
        user = request.user
        
        if review_type == 'tenant_to_property':
            if not hasattr(user, 'tenant_profile'):
                raise serializers.ValidationError(
                    'Only tenants can review properties.'
                )
            if lease.tenant.user != user:
                raise serializers.ValidationError(
                    'You can only review properties you have rented.'
                )
            attrs['property'] = lease.unit.property
            attrs['tenant'] = None
            
        elif review_type == 'owner_to_tenant':
            if not hasattr(user, 'owner_profile'):
                raise serializers.ValidationError(
                    'Only owners can review tenants.'
                )
            if lease.unit.property.owner.user != user:
                raise serializers.ValidationError(
                    'You can only review your own tenants.'
                )
            attrs['tenant'] = lease.tenant
            attrs['property'] = None
        
        return attrs
    
    def create(self, validated_data):
        validated_data['reviewer'] = self.context['request'].user
        return Review.objects.create(**validated_data)


class ReviewResponseSerializer(serializers.Serializer):
    """Serializer for responding to reviews."""
    response = serializers.CharField()


# ==================== Notification Serializers ====================

class NotificationSerializer(serializers.ModelSerializer):
    """Notification serializer."""
    notification_type_display = serializers.CharField(
        source='get_notification_type_display', read_only=True
    )
    message_localized = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = ['id', 'notification_type', 'notification_type_display',
                  'title', 'message', 'message_swahili', 'message_localized',
                  'is_read', 'created_at', 'action_url']
        read_only_fields = ['id', 'created_at']
    
    def get_message_localized(self, obj):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.get_message(request.user.preferred_language)
        return obj.message


# ==================== Dashboard Serializers ====================

class TenantDashboardSerializer(serializers.Serializer):
    """Dashboard stats for tenants."""
    active_leases = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    total_paid_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    upcoming_due_payments = serializers.ListField()
    open_maintenance_requests = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()


class OwnerDashboardSerializer(serializers.Serializer):
    """Dashboard stats for owners."""
    total_properties = serializers.IntegerField()
    total_units = serializers.IntegerField()
    occupied_units = serializers.IntegerField()
    vacancy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    active_leases = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    revenue_this_month = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_maintenance = serializers.IntegerField()
    recent_payments = serializers.ListField()
    expiring_leases = serializers.ListField()
    unread_notifications = serializers.IntegerField()


class AdminDashboardSerializer(serializers.Serializer):
    """Dashboard stats for admins."""
    total_users = serializers.IntegerField()
    total_tenants = serializers.IntegerField()
    total_owners = serializers.IntegerField()
    total_properties = serializers.IntegerField()
    total_units = serializers.IntegerField()
    active_leases = serializers.IntegerField()
    pending_verifications = serializers.IntegerField()
    payments_this_month = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_payment_verifications = serializers.IntegerField()
