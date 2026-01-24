from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal


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
        default=Decimal('0.00'),
        help_text='Total earnings in TZS'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Owner: {self.user.get_full_name()}"
    
    def update_property_count(self):
        self.total_properties = self.properties.count()
        self.save(update_fields=['total_properties'])


class Location(models.Model):
    """Location model with Tanzanian administrative hierarchy."""
    
    REGION_CHOICES = [
        ('dar_es_salaam', 'Dar es Salaam'),
        ('arusha', 'Arusha'),
        ('dodoma', 'Dodoma'),
        ('mwanza', 'Mwanza'),
        ('tanga', 'Tanga'),
        ('morogoro', 'Morogoro'),
        ('mbeya', 'Mbeya'),
        ('kilimanjaro', 'Kilimanjaro'),
        ('iringa', 'Iringa'),
        ('kagera', 'Kagera'),
        ('kigoma', 'Kigoma'),
        ('lindi', 'Lindi'),
        ('mara', 'Mara'),
        ('mtwara', 'Mtwara'),
        ('pwani', 'Pwani'),
        ('rukwa', 'Rukwa'),
        ('ruvuma', 'Ruvuma'),
        ('shinyanga', 'Shinyanga'),
        ('singida', 'Singida'),
        ('tabora', 'Tabora'),
        ('zanzibar', 'Zanzibar'),
        ('pemba', 'Pemba'),
        ('geita', 'Geita'),
        ('katavi', 'Katavi'),
        ('njombe', 'Njombe'),
        ('simiyu', 'Simiyu'),
        ('songwe', 'Songwe'),
    ]
    
    region = models.CharField(max_length=50, choices=REGION_CHOICES)
    district = models.CharField(max_length=100)
    ward = models.CharField(max_length=100)
    street_address = models.CharField(max_length=255)
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True
    )
    landmark = models.CharField(
        max_length=255, 
        blank=True,
        help_text='Nearby landmark for easy identification'
    )
    
    class Meta:
        ordering = ['region', 'district', 'ward']
    
    def __str__(self):
        return f"{self.street_address}, {self.ward}, {self.district}, {self.get_region_display()}"


class Property(models.Model):
    """Property model for rental listings."""
    
    PROPERTY_TYPE_CHOICES = [
        ('room', 'Room/Chumba'),
        ('house', 'House/Nyumba'),
        ('apartment', 'Apartment/Fleti'),
        ('shop', 'Shop/Duka'),
        ('office', 'Office/Ofisi'),
        ('warehouse', 'Warehouse/Godown'),
        ('land', 'Land/Kiwanja'),
        ('commercial', 'Commercial Building'),
    ]
    
    owner = models.ForeignKey(
        Owner, 
        on_delete=models.CASCADE, 
        related_name='properties'
    )
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    monthly_rent = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Monthly rent in TZS'
    )
    location = models.OneToOneField(
        Location, 
        on_delete=models.CASCADE, 
        related_name='property'
    )
    total_rooms = models.PositiveIntegerField(default=1)
    available_rooms = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    listed_date = models.DateField(auto_now_add=True)
    rules_terms = models.TextField(
        blank=True,
        help_text='Property rules and terms'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-listed_date']
    
    def __str__(self):
        return f"{self.title} - {self.location.district}"
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return None


class PropertyImage(models.Model):
    """Property images model."""
    
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='images'
    )
    image = models.ImageField(upload_to='property_images/%Y/%m/')
    caption = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', '-uploaded_at']
    
    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyAmenity(models.Model):
    """Amenities specific to Tanzanian market."""
    
    AMENITY_CHOICES = [
        ('water_24h', '24/7 Water Supply'),
        ('water_tank', 'Water Tank'),
        ('borehole', 'Borehole'),
        ('electricity', 'TANESCO Electricity'),
        ('solar', 'Solar Power'),
        ('generator', 'Generator Backup'),
        ('security_guard', 'Security Guard/Mlinzi'),
        ('cctv', 'CCTV Cameras'),
        ('parking', 'Parking Space'),
        ('fence', 'Fenced Compound'),
        ('toilet_inside', 'Inside Toilet'),
        ('toilet_outside', 'Outside Toilet'),
        ('kitchen_inside', 'Inside Kitchen'),
        ('kitchen_outside', 'Outside Kitchen'),
        ('furnished', 'Furnished'),
        ('tiles', 'Tiled Floor'),
        ('ceiling', 'Ceiling'),
        ('balcony', 'Balcony'),
        ('garden', 'Garden'),
        ('wifi', 'WiFi Available'),
    ]
    
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='amenities'
    )
    amenity = models.CharField(max_length=30, choices=AMENITY_CHOICES)
    
    class Meta:
        verbose_name_plural = 'Property Amenities'
        unique_together = ['property', 'amenity']
    
    def __str__(self):
        return f"{self.property.title} - {self.get_amenity_display()}"


class RentalUnit(models.Model):
    """Individual rental units within a property."""
    
    UNIT_TYPE_CHOICES = [
        ('single_room', 'Single Room/Chumba Kimoja'),
        ('double_room', 'Double Room/Vyumba Viwili'),
        ('bedsitter', 'Bedsitter'),
        ('one_bedroom', 'One Bedroom'),
        ('two_bedroom', 'Two Bedroom'),
        ('three_bedroom', 'Three Bedroom'),
        ('shop_unit', 'Shop Unit'),
        ('office_unit', 'Office Unit'),
        ('warehouse_unit', 'Warehouse Unit'),
    ]
    
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='units'
    )
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES)
    unit_number = models.CharField(max_length=20)
    unit_rent = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Monthly rent for this unit in TZS'
    )
    area_sqm = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text='Area in square meters'
    )
    is_occupied = models.BooleanField(default=False)
    unit_features = models.TextField(
        blank=True,
        help_text='Specific features of this unit'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['property', 'unit_number']
        ordering = ['property', 'unit_number']
    
    def __str__(self):
        return f"{self.property.title} - Unit {self.unit_number}"


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
    
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='leases'
    )
    unit = models.ForeignKey(
        RentalUnit, 
        on_delete=models.CASCADE, 
        related_name='leases'
    )
    start_date = models.DateField()
    end_date = models.DateField()
    monthly_rent = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Agreed monthly rent in TZS'
    )
    security_deposit = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Security deposit in TZS'
    )
    payment_frequency = models.CharField(
        max_length=20, 
        choices=PAYMENT_FREQUENCY_CHOICES, 
        default='monthly'
    )
    payment_due_day = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(28)],
        help_text='Day of month rent is due'
    )
    terms_conditions = models.TextField(
        blank=True,
        help_text='Additional terms and conditions'
    )
    agreement_document = models.FileField(
        upload_to='lease_documents/%Y/%m/', 
        blank=True, 
        null=True
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='draft'
    )
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
    
    lease = models.ForeignKey(
        LeaseAgreement, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    owner = models.ForeignKey(
        Owner, 
        on_delete=models.CASCADE, 
        related_name='received_payments'
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Amount in TZS'
    )
    payment_date = models.DateField(null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_status = models.CharField(
        max_length=25, 
        choices=PAYMENT_STATUS_CHOICES, 
        default='pending'
    )
    mobile_money_code = models.CharField(
        max_length=30, 
        blank=True,
        help_text='M-Pesa/Mobile Money confirmation code'
    )
    due_date = models.DateField()
    payment_period = models.CharField(
        max_length=50,
        help_text='e.g., January 2026, Q1 2026'
    )
    receipt_number = models.CharField(max_length=50, blank=True)
    receipt_file = models.FileField(
        upload_to='receipts/%Y/%m/', 
        blank=True, 
        null=True
    )
    notes = models.TextField(blank=True)
    verified_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
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
    
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='maintenance_requests'
    )
    unit = models.ForeignKey(
        RentalUnit, 
        on_delete=models.CASCADE, 
        related_name='maintenance_requests'
    )
    owner = models.ForeignKey(
        Owner, 
        on_delete=models.CASCADE, 
        related_name='maintenance_requests'
    )
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE_CHOICES)
    description = models.TextField()
    priority = models.CharField(
        max_length=20, 
        choices=PRIORITY_CHOICES, 
        default='medium'
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='submitted'
    )
    request_date = models.DateTimeField(auto_now_add=True)
    acknowledged_date = models.DateTimeField(null=True, blank=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    cost = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
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


class Review(models.Model):
    """Review model for two-way rating system."""
    
    REVIEW_TYPE_CHOICES = [
        ('tenant_to_property', 'Tenant reviewing Property'),
        ('owner_to_tenant', 'Owner reviewing Tenant'),
    ]
    
    review_type = models.CharField(max_length=30, choices=REVIEW_TYPE_CHOICES)
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews_written'
    )
    tenant = models.ForeignKey(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='reviews_received',
        null=True,
        blank=True,
        help_text='For owner reviewing tenant'
    )
    property = models.ForeignKey(
        Property, 
        on_delete=models.CASCADE, 
        related_name='reviews',
        null=True,
        blank=True,
        help_text='For tenant reviewing property'
    )
    lease = models.ForeignKey(
        LeaseAgreement,
        on_delete=models.CASCADE,
        related_name='reviews',
        help_text='Verified lease for this review'
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    response_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='review_responses'
    )
    is_visible = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-review_date']
    
    def __str__(self):
        return f"Review by {self.reviewer.get_full_name()} - {self.rating} stars"


class Notification(models.Model):
    """Notification model for user notifications."""
    
    NOTIFICATION_TYPE_CHOICES = [
        ('rent_reminder_7', 'Rent Reminder (7 days)'),
        ('rent_reminder_3', 'Rent Reminder (3 days)'),
        ('rent_due', 'Rent Due Today'),
        ('rent_overdue', 'Rent Overdue'),
        ('payment_received', 'Payment Received'),
        ('payment_verified', 'Payment Verified'),
        ('payment_rejected', 'Payment Rejected'),
        ('lease_expiring', 'Lease Expiring'),
        ('lease_renewed', 'Lease Renewed'),
        ('lease_created', 'Lease Created'),
        ('maintenance_submitted', 'Maintenance Request Submitted'),
        ('maintenance_acknowledged', 'Maintenance Acknowledged'),
        ('maintenance_in_progress', 'Maintenance In Progress'),
        ('maintenance_completed', 'Maintenance Completed'),
        ('new_review', 'New Review'),
        ('review_response', 'Review Response'),
        ('document_verified', 'Document Verified'),
        ('account_verified', 'Account Verified'),
        ('general', 'General Notification'),
    ]
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='notifications'
    )
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    message_swahili = models.TextField(
        blank=True,
        help_text='Swahili translation of the message'
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    action_url = models.CharField(max_length=255, blank=True)
    related_object_type = models.CharField(max_length=50, blank=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.get_full_name()}"
    
    def get_message(self, language='en'):
        if language == 'sw' and self.message_swahili:
            return self.message_swahili
        return self.message
