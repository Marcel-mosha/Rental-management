from rest_framework import serializers


# ==================== Dashboard Serializers ====================

class TenantDashboardSerializer(serializers.Serializer):
    """Dashboard stats for tenants."""
    active_leases = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    total_paid_this_month = serializers.DecimalField(max_digits=12, decimal_places=2)
    upcoming_due_payments = serializers.ListField()
    open_maintenance_requests = serializers.IntegerField()
    unread_notifications = serializers.IntegerField()


class OwnerDashboardSerializer(serializers.Serializer):
    """Dashboard stats for owners."""
    total_properties = serializers.IntegerField()
    total_units = serializers.IntegerField()
    occupied_units = serializers.IntegerField()
    vacancy_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
    active_leases = serializers.IntegerField()
    pending_payments = serializers.IntegerField()
    revenue_this_month = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_maintenance = serializers.IntegerField()
    recent_payments = serializers.ListField()
    expiring_leases = serializers.ListField()
    unread_notifications = serializers.IntegerField()


class AdminDashboardSerializer(serializers.Serializer):
    """Dashboard stats for admins."""
    total_users = serializers.IntegerField()
    total_tenants = serializers.IntegerField()
    total_owners = serializers.IntegerField()
    total_properties = serializers.IntegerField()
    total_units = serializers.IntegerField()
    active_leases = serializers.IntegerField()
    pending_verifications = serializers.IntegerField()
    payments_this_month = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_payment_verifications = serializers.IntegerField()
