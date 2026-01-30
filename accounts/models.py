from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom User model with Tanzanian-specific fields."""
    
    USER_TYPE_CHOICES = [
        ('admin', 'Administrator'),
        ('tenant', 'Tenant'),
        ('owner', 'Property Owner'),
    ]
    
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='tenant'
    )
    phone_number = models.CharField(
        max_length=15, 
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^\+?255\d{9}$',
                message='Enter a valid Tanzanian phone number (e.g., +255XXXXXXXXX)'
            )
        ]
    )
    profile_image = models.ImageField(
        upload_to='profiles/%Y/%m/', 
        blank=True, 
        null=True
    )
    registration_date = models.DateField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verification_document = models.FileField(
        upload_to='verification_docs/%Y/%m/', 
        blank=True, 
        null=True
    )
    preferred_language = models.CharField(
        max_length=10,
        choices=[('en', 'English'), ('sw', 'Swahili')],
        default='en'
    )
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.user_type})"


class Document(models.Model):
    """Document model for storing user verification documents."""
    
    DOCUMENT_TYPE_CHOICES = [
        ('nida', 'NIDA ID'),
        ('tin', 'TIN Certificate'),
        ('passport', 'Passport'),
        ('driving_license', 'Driving License'),
        ('business_license', 'Business License'),
        ('lease_agreement', 'Lease Agreement'),
        ('receipt', 'Payment Receipt'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    document_type = models.CharField(max_length=30, choices=DOCUMENT_TYPE_CHOICES)
    document_file = models.FileField(upload_to='documents/%Y/%m/')
    upload_date = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    verification_notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-upload_date']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.get_document_type_display()}"


class Tenant(models.Model):
    """Tenant profile model."""
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='tenant_profile'
    )
    occupation = models.CharField(max_length=100, blank=True)
    employer_name = models.CharField(max_length=200, blank=True)
    monthly_income = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Monthly income in TZS'
    )
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    reference_name = models.CharField(max_length=200, blank=True)
    reference_contact = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Tenant: {self.user.get_full_name()}"


class Owner(models.Model):
    """Property Owner profile model."""
    
    BANK_CHOICES = [
        ('crdb', 'CRDB Bank'),
        ('nmb', 'NMB Bank'),
        ('nbc', 'NBC Bank'),
        ('stanbic', 'Stanbic Bank'),
        ('equity', 'Equity Bank'),
        ('kcb', 'KCB Bank'),
        ('dtb', 'DTB Bank'),
        ('exim', 'Exim Bank'),
        ('azania', 'Azania Bank'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='owner_profile'
    )
    company_name = models.CharField(max_length=200, blank=True)
    tax_identification_number = models.CharField(
        max_length=20, 
        blank=True,
        help_text='TIN number for TRA compliance'
    )
    bank_name = models.CharField(max_length=50, choices=BANK_CHOICES, blank=True)
    account_number = models.CharField(max_length=30, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    total_properties = models.PositiveIntegerField(default=0)
    total_earnings = models.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        default=0.00,
        help_text='Total earnings in TZS'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Owner: {self.user.get_full_name()}"
    
    def update_property_count(self):
        # Import here to avoid circular dependency
        from properties.models import Property
        self.total_properties = Property.objects.filter(owner=self).count()
        self.save(update_fields=['total_properties'])
