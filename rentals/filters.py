import django_filters
from django.db.models import Q
from .models import (
    Property, RentalUnit, LeaseAgreement, Payment, MaintenanceRequest
)


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


class LeaseFilter(django_filters.FilterSet):
    """Filter for LeaseAgreement model."""
    
    # Date range filters
    start_date_from = django_filters.DateFilter(
        field_name='start_date', lookup_expr='gte'
    )
    start_date_to = django_filters.DateFilter(
        field_name='start_date', lookup_expr='lte'
    )
    end_date_from = django_filters.DateFilter(
        field_name='end_date', lookup_expr='gte'
    )
    end_date_to = django_filters.DateFilter(
        field_name='end_date', lookup_expr='lte'
    )
    
    # Rent range
    min_rent = django_filters.NumberFilter(
        field_name='monthly_rent', lookup_expr='gte'
    )
    max_rent = django_filters.NumberFilter(
        field_name='monthly_rent', lookup_expr='lte'
    )
    
    # Related filters
    tenant = django_filters.NumberFilter(field_name='tenant_id')
    property_id = django_filters.NumberFilter(field_name='unit__property_id')
    owner = django_filters.NumberFilter(field_name='unit__property__owner_id')
    
    # Expiring soon filter
    expiring_within_days = django_filters.NumberFilter(
        method='filter_expiring_within'
    )
    
    class Meta:
        model = LeaseAgreement
        fields = [
            'status', 'payment_frequency', 'deposit_paid',
            'start_date_from', 'start_date_to', 'end_date_from', 'end_date_to',
            'min_rent', 'max_rent', 'tenant', 'property_id', 'owner',
            'expiring_within_days'
        ]
    
    def filter_expiring_within(self, queryset, name, value):
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        future_date = today + timedelta(days=value)
        return queryset.filter(
            status='active',
            end_date__gte=today,
            end_date__lte=future_date
        )


class PaymentFilter(django_filters.FilterSet):
    """Filter for Payment model."""
    
    # Date range filters
    payment_date_from = django_filters.DateFilter(
        field_name='payment_date', lookup_expr='gte'
    )
    payment_date_to = django_filters.DateFilter(
        field_name='payment_date', lookup_expr='lte'
    )
    due_date_from = django_filters.DateFilter(
        field_name='due_date', lookup_expr='gte'
    )
    due_date_to = django_filters.DateFilter(
        field_name='due_date', lookup_expr='lte'
    )
    
    # Amount range
    min_amount = django_filters.NumberFilter(
        field_name='amount', lookup_expr='gte'
    )
    max_amount = django_filters.NumberFilter(
        field_name='amount', lookup_expr='lte'
    )
    
    # Related filters
    lease = django_filters.NumberFilter(field_name='lease_id')
    tenant = django_filters.NumberFilter(field_name='tenant_id')
    owner = django_filters.NumberFilter(field_name='owner_id')
    property_id = django_filters.NumberFilter(
        field_name='lease__unit__property_id'
    )
    
    # Overdue filter
    is_overdue = django_filters.BooleanFilter(method='filter_is_overdue')
    
    # Period filter
    payment_period = django_filters.CharFilter(
        field_name='payment_period', lookup_expr='icontains'
    )
    
    class Meta:
        model = Payment
        fields = [
            'payment_status', 'payment_method',
            'payment_date_from', 'payment_date_to',
            'due_date_from', 'due_date_to',
            'min_amount', 'max_amount',
            'lease', 'tenant', 'owner', 'property_id',
            'is_overdue', 'payment_period'
        ]
    
    def filter_is_overdue(self, queryset, name, value):
        from django.utils import timezone
        today = timezone.now().date()
        
        if value:
            return queryset.filter(
                payment_status='pending',
                due_date__lt=today
            )
        return queryset.exclude(
            payment_status='pending',
            due_date__lt=today
        )


class MaintenanceRequestFilter(django_filters.FilterSet):
    """Filter for MaintenanceRequest model."""
    
    # Date range filters
    request_date_from = django_filters.DateTimeFilter(
        field_name='request_date', lookup_expr='gte'
    )
    request_date_to = django_filters.DateTimeFilter(
        field_name='request_date', lookup_expr='lte'
    )
    resolved_date_from = django_filters.DateTimeFilter(
        field_name='resolved_date', lookup_expr='gte'
    )
    resolved_date_to = django_filters.DateTimeFilter(
        field_name='resolved_date', lookup_expr='lte'
    )
    
    # Cost range
    min_cost = django_filters.NumberFilter(
        field_name='cost', lookup_expr='gte'
    )
    max_cost = django_filters.NumberFilter(
        field_name='cost', lookup_expr='lte'
    )
    
    # Related filters
    tenant = django_filters.NumberFilter(field_name='tenant_id')
    owner = django_filters.NumberFilter(field_name='owner_id')
    unit = django_filters.NumberFilter(field_name='unit_id')
    property_id = django_filters.NumberFilter(field_name='unit__property_id')
    
    # Multiple status/priority filter
    statuses = django_filters.CharFilter(method='filter_multiple_statuses')
    priorities = django_filters.CharFilter(method='filter_multiple_priorities')
    
    class Meta:
        model = MaintenanceRequest
        fields = [
            'issue_type', 'priority', 'status', 'cost_responsibility',
            'request_date_from', 'request_date_to',
            'resolved_date_from', 'resolved_date_to',
            'min_cost', 'max_cost',
            'tenant', 'owner', 'unit', 'property_id',
            'statuses', 'priorities'
        ]
    
    def filter_multiple_statuses(self, queryset, name, value):
        status_list = value.split(',')
        return queryset.filter(status__in=status_list)
    
    def filter_multiple_priorities(self, queryset, name, value):
        priority_list = value.split(',')
        return queryset.filter(priority__in=priority_list)
