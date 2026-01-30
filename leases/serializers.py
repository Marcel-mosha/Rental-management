from rest_framework import serializers
from .models import LeaseAgreement
from accounts.serializers import TenantListSerializer
from properties.serializers import RentalUnitSerializer
from properties.models import RentalUnit
from accounts.models import Tenant


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
            'address': str(obj.unit.property.locality)
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
