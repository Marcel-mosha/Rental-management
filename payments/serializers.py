from rest_framework import serializers
from .models import Payment
from accounts.serializers import TenantListSerializer, OwnerListSerializer
from leases.models import LeaseAgreement


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
