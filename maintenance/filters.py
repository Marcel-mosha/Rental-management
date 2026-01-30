import django_filters
from .models import MaintenanceRequest


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
