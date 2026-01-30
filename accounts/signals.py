from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Tenant, Owner, LeaseAgreement, RentalUnit, Property

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create tenant or owner profile based on user_type when user is created."""
    if created:
        if instance.user_type == 'tenant':
            Tenant.objects.get_or_create(user=instance)
        elif instance.user_type == 'owner':
            Owner.objects.get_or_create(user=instance)


@receiver(post_save, sender=LeaseAgreement)
def update_unit_status_on_lease_change(sender, instance, **kwargs):
    """Update rental unit occupancy status when lease status changes."""
    unit = instance.unit
    
    if instance.status == 'active':
        unit.is_occupied = True
    elif instance.status in ['terminated', 'expired']:
        # Check if there are other active leases for this unit
        other_active_leases = LeaseAgreement.objects.filter(
            unit=unit, status='active'
        ).exclude(pk=instance.pk).exists()
        
        if not other_active_leases:
            unit.is_occupied = False
    
    unit.save(update_fields=['is_occupied'])


@receiver(post_save, sender=RentalUnit)
def update_property_available_rooms(sender, instance, **kwargs):
    """Update property's available rooms count when unit status changes."""
    property_obj = instance.property
    property_obj.available_rooms = property_obj.units.filter(
        is_occupied=False
    ).count()
    property_obj.save(update_fields=['available_rooms'])


@receiver(post_save, sender=Property)
def update_owner_property_count(sender, instance, created, **kwargs):
    """Update owner's total property count when property is created/deleted."""
    if created:
        instance.owner.update_property_count()
