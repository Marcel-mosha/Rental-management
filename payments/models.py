from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import User, Tenant, Owner
from leases.models import LeaseAgreement


class Payment(models.Model):
    """Payment model with Tanzanian payment methods."""
    
    PAYMENT_METHOD_CHOICES = [
        ('mpesa', 'M-Pesa'),
        ('tigopesa', 'Tigo Pesa'),
        ('airtelmoney', 'Airtel Money'),
        ('halopesa', 'Halo Pesa'),
        ('bank_transfer', 'Bank Transfer'),
        ('cash', 'Cash'),
        ('cheque', 'Cheque'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('pending_verification', 'Pending Verification'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
        ('cancelled', 'Cancelled'),
    ]
    
    lease = models.ForeignKey(LeaseAgreement, on_delete=models.CASCADE, related_name='payments')
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='payments')
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='received_payments')
    amount = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Amount in TZS'
    )
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default='pending')
    mobile_money_code = models.CharField(
        max_length=30, blank=True,
        help_text='M-Pesa/Mobile Money confirmation code'
    )
    due_date = models.DateField()
    payment_period = models.CharField(max_length=50, help_text='e.g., January 2026, Q1 2026')
    receipt_number = models.CharField(max_length=50, blank=True)
    receipt_file = models.FileField(upload_to='receipts/%Y/%m/', blank=True, null=True)
    notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='verified_payments'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-due_date', '-created_at']
    
    def __str__(self):
        return f"Payment: {self.tenant.user.get_full_name()} - TZS {self.amount}"
    
    @property
    def is_late(self):
        from django.utils import timezone
        if self.payment_status == 'completed' and self.payment_date:
            return self.payment_date > self.due_date
        return timezone.now().date() > self.due_date
    
    def generate_receipt_number(self):
        from django.utils import timezone
        import random
        timestamp = timezone.now().strftime('%Y%m%d%H%M')
        random_digits = random.randint(1000, 9999)
        self.receipt_number = f"RCP-{timestamp}-{random_digits}"
        return self.receipt_number
