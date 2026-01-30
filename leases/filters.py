import django_filters
from .models import LeaseAgreement


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
