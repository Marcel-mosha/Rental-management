import django_filters
from .models import Payment


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
