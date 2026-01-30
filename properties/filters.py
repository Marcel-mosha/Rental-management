import django_filters
from .models import Property, RentalUnit


class PropertyFilter(django_filters.FilterSet):
    """Filter for Property model with Tanzanian-specific fields."""
    
    # Rent range
    min_rent = django_filters.NumberFilter(
        field_name='monthly_rent', lookup_expr='gte'
    )
    max_rent = django_filters.NumberFilter(
        field_name='monthly_rent', lookup_expr='lte'
    )
    
    # Location filters
    region = django_filters.CharFilter(
        field_name='location__region', lookup_expr='exact'
    )
    district = django_filters.CharFilter(
        field_name='location__district', lookup_expr='icontains'
    )
    ward = django_filters.CharFilter(
        field_name='location__ward', lookup_expr='icontains'
    )
    
    # Room filters
    min_rooms = django_filters.NumberFilter(
        field_name='total_rooms', lookup_expr='gte'
    )
    max_rooms = django_filters.NumberFilter(
        field_name='total_rooms', lookup_expr='lte'
    )
    has_available_rooms = django_filters.BooleanFilter(
        method='filter_has_available_rooms'
    )
    
    # Amenity filter
    amenities = django_filters.CharFilter(method='filter_by_amenities')
    
    # Owner filter
    owner = django_filters.NumberFilter(field_name='owner_id')
    
    class Meta:
        model = Property
        fields = [
            'property_type', 'is_available', 'owner',
            'min_rent', 'max_rent', 'region', 'district', 'ward',
            'min_rooms', 'max_rooms', 'has_available_rooms', 'amenities'
        ]
    
    def filter_has_available_rooms(self, queryset, name, value):
        if value:
            return queryset.filter(available_rooms__gt=0)
        return queryset.filter(available_rooms=0)
    
    def filter_by_amenities(self, queryset, name, value):
        """Filter properties that have all specified amenities."""
        amenity_list = value.split(',')
        for amenity in amenity_list:
            queryset = queryset.filter(amenities__amenity=amenity.strip())
        return queryset.distinct()


class RentalUnitFilter(django_filters.FilterSet):
    """Filter for RentalUnit model."""
    
    # Property filter
    property_id = django_filters.NumberFilter(field_name='property_id')
    
    # Rent range
    min_rent = django_filters.NumberFilter(
        field_name='unit_rent', lookup_expr='gte'
    )
    max_rent = django_filters.NumberFilter(
        field_name='unit_rent', lookup_expr='lte'
    )
    
    # Area range
    min_area = django_filters.NumberFilter(
        field_name='area_sqm', lookup_expr='gte'
    )
    max_area = django_filters.NumberFilter(
        field_name='area_sqm', lookup_expr='lte'
    )
    
    # Location filters (through property)
    region = django_filters.CharFilter(
        field_name='property__location__region', lookup_expr='exact'
    )
    district = django_filters.CharFilter(
        field_name='property__location__district', lookup_expr='icontains'
    )
    
    class Meta:
        model = RentalUnit
        fields = [
            'property_id', 'unit_type', 'is_occupied',
            'min_rent', 'max_rent', 'min_area', 'max_area',
            'region', 'district'
        ]
