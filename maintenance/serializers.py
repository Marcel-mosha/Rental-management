from rest_framework import serializers
from .models import MaintenanceRequest, MaintenanceImage
from accounts.serializers import TenantListSerializer, OwnerListSerializer
from properties.serializers import RentalUnitListSerializer
from properties.models import RentalUnit


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
