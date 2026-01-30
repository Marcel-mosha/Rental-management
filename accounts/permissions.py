from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Permission check for property owners."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (hasattr(request.user, 'owner_profile') or request.user.is_staff)
        )


class IsTenant(permissions.BasePermission):
    """Permission check for tenants."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            (hasattr(request.user, 'tenant_profile') or request.user.is_staff)
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Permission for owners or admins."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_staff or 
            hasattr(request.user, 'owner_profile')
        )


class IsTenantOrAdmin(permissions.BasePermission):
    """Permission for tenants or admins."""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return (
            request.user.is_staff or 
            hasattr(request.user, 'tenant_profile')
        )


class IsPropertyOwner(permissions.BasePermission):
    """Permission check for property-specific actions (owner only)."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # For Property objects
        if hasattr(obj, 'owner'):
            return obj.owner.user == request.user
        
        # For RentalUnit objects
        if hasattr(obj, 'property'):
            return obj.property.owner.user == request.user
        
        return False


class IsLeaseParticipant(permissions.BasePermission):
    """Permission for lease participants (tenant, owner, or admin)."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Check if user is the tenant
        if hasattr(request.user, 'tenant_profile'):
            if obj.tenant == request.user.tenant_profile:
                return True
        
        # Check if user is the property owner
        if hasattr(request.user, 'owner_profile'):
            if obj.unit.property.owner == request.user.owner_profile:
                return True
        
        return False


class IsPaymentParticipant(permissions.BasePermission):
    """Permission for payment participants (tenant, owner, or admin)."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Check if user is the tenant
        if hasattr(request.user, 'tenant_profile'):
            if obj.tenant == request.user.tenant_profile:
                return True
        
        # Check if user is the owner
        if hasattr(request.user, 'owner_profile'):
            if obj.owner == request.user.owner_profile:
                return True
        
        return False


class IsMaintenanceParticipant(permissions.BasePermission):
    """Permission for maintenance request participants."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        # Tenant can view and create
        if hasattr(request.user, 'tenant_profile'):
            if obj.tenant == request.user.tenant_profile:
                # Tenant can only view and create, not update status
                if view.action in ['update_status']:
                    return False
                return True
        
        # Owner can view and update
        if hasattr(request.user, 'owner_profile'):
            if obj.owner == request.user.owner_profile:
                return True
        
        return False


class CanVerifyPayment(permissions.BasePermission):
    """Permission to verify payments (owner of the property or admin)."""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        
        if hasattr(request.user, 'owner_profile'):
            return obj.owner == request.user.owner_profile
        
        return False
