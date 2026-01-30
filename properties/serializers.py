from rest_framework import serializers
from .models import Property, PropertyImage, PropertyAmenity, RentalUnit
from accounts.serializers import OwnerListSerializer
from localities.serializers import LocalitySerializer


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
    locality = serializers.SerializerMethodField()
    property_type_display = serializers.CharField(
        source='get_property_type_display', read_only=True
    )
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = ['id', 'title', 'property_type', 'property_type_display',
                  'monthly_rent', 'locality', 'owner_name',
                  'available_rooms', 'total_rooms', 'is_available',
                  'average_rating', 'primary_image', 'listed_date']
    
    def get_owner_name(self, obj):
        return obj.owner.user.get_full_name()
    
    def get_locality(self, obj):
        return f"{obj.locality}"
    
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
    from accounts.models import Owner
    
    owner = OwnerListSerializer(read_only=True)
    owner_id = serializers.PrimaryKeyRelatedField(
        queryset=Owner.objects.all(), 
        source='owner', write_only=True
    )
    locality = LocalitySerializer()
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
                  'title', 'description', 'monthly_rent', 'locality',
                  'total_rooms', 'available_rooms', 'is_available', 'listed_date',
                  'rules_terms', 'images', 'amenities', 'units', 'average_rating',
                  'reviews_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'listed_date', 'created_at', 'updated_at']
    
    def get_reviews_count(self, obj):
        return obj.reviews.filter(is_visible=True).count()
    
    def create(self, validated_data):
        from localities.models import Locality
        locality_data = validated_data.pop('locality')
        locality = Locality.objects.create(**locality_data)
        property_obj = Property.objects.create(locality=locality, **validated_data)
        return property_obj
    
    def update(self, instance, validated_data):
        locality_data = validated_data.pop('locality', None)
        if locality_data:
            for attr, value in locality_data.items():
                setattr(instance.locality, attr, value)
            instance.locality.save()
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PropertyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating properties."""
    locality = LocalitySerializer()
    amenities = serializers.ListField(
        child=serializers.CharField(), write_only=True, required=False
    )
    
    class Meta:
        model = Property
        fields = ['property_type', 'title', 'description', 'monthly_rent',
                  'locality', 'total_rooms', 'available_rooms', 'rules_terms',
                  'amenities']
    
    def create(self, validated_data):
        from localities.models import Locality
        locality_data = validated_data.pop('locality')
        amenities_data = validated_data.pop('amenities', [])
        
        locality = Locality.objects.create(**locality_data)
        
        # Get owner from context (current user)
        owner = self.context['request'].user.owner_profile
        property_obj = Property.objects.create(
            owner=owner, 
            locality=locality, 
            **validated_data
        )
        
        # Create amenities
        for amenity_code in amenities_data:
            PropertyAmenity.objects.create(property=property_obj, amenity=amenity_code)
        
        return property_obj
