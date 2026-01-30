from rest_framework import serializers
from .models import Review
from accounts.serializers import UserListSerializer
from leases.models import LeaseAgreement


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
