from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from accounts.models import Tenant
from properties.models import RentalUnit


class LeaseAgreement(models.Model):
    """Lease agreement model following Tanzanian tenancy laws."""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending Signature'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('renewed', 'Renewed'),
    ]
    
    PAYMENT_FREQUENCY_CHOICES = [
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly (3 months)'),
        ('biannual', 'Bi-Annual (6 months)'),
        ('annual', 'Annual (12 months)'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='leases')
    unit = models.ForeignKey(RentalUnit, on_delete=models.CASCADE, related_name='leases')
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Agreed monthly rent in TZS'
    )
    security_deposit = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Security deposit in TZS'
    )
    payment_frequency = models.CharField(
        max_length=20, choices=PAYMENT_FREQUENCY_CHOICES, default='monthly'
    )
    payment_due_day = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(28)],
        help_text='Day of month rent is due'
    )
    terms_conditions = models.TextField(blank=True, help_text='Additional terms and conditions')
    agreement_document = models.FileField(upload_to='lease_documents/%Y/%m/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    signed_date = models.DateField(null=True, blank=True)
    deposit_paid = models.BooleanField(default=False)
    deposit_paid_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return f"Lease: {self.tenant.user.get_full_name()} - {self.unit}"
    
    @property
    def is_active(self):
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date and self.status == 'active'
    
    @property
    def owner(self):
        return self.unit.property.owner
