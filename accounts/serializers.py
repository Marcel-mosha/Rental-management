from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import Document, Tenant, Owner

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
        from leases.models import LeaseAgreement
        return LeaseAgreement.objects.filter(tenant=obj, status='active').count()


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
