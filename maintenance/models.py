from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import Tenant, Owner
from properties.models import RentalUnit


class MaintenanceRequest(models.Model):
    """Maintenance request model."""
    
    ISSUE_TYPE_CHOICES = [
        ('plumbing', 'Plumbing/Mabomba'),
        ('electrical', 'Electrical/Umeme'),
        ('structural', 'Structural/Ujenzi'),
        ('appliance', 'Appliance/Vifaa'),
        ('pest', 'Pest Control/Wadudu'),
        ('cleaning', 'Cleaning/Usafi'),
        ('security', 'Security/Usalama'),
        ('water', 'Water Supply/Maji'),
        ('toilet', 'Toilet/Choo'),
        ('roof', 'Roof/Paa'),
        ('door_window', 'Door/Window'),
        ('painting', 'Painting/Rangi'),
        ('other', 'Other/Nyingine'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low/Kawaida'),
        ('medium', 'Medium/Wastani'),
        ('high', 'High/Haraka'),
        ('urgent', 'Urgent/Dharura'),
    ]
    
    STATUS_CHOICES = [
        ('submitted', 'Submitted'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='maintenance_requests')
    unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE, related_name='maintenance_requests')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='maintenance_requests')
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE_CHOICES)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    request_date = models.DateTimeField(auto_now_add=True)
    acknowledged_date = models.DateTimeField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True,
        help_text='Repair cost in TZS'
    )
    cost_responsibility = models.CharField(
        max_length=20,
        choices=[('tenant', 'Tenant'), ('owner', 'Owner'), ('shared', 'Shared')],
        default='owner'
    )
    technician_name = models.CharField(max_length=200, blank=True)
    technician_contact = models.CharField(max_length=15, blank=True)
    resolution_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-request_date']
    
    def __str__(self):
        return f"{self.get_issue_type_display()} - {self.unit}"


class MaintenanceImage(models.Model):
    """Images for maintenance requests."""
    
    maintenance_request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image = models.ImageField(upload_to='maintenance_images/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.maintenance_request}"
