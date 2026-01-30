from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from accounts.models import Owner
from localities.models import Locality


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
    
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='properties')
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    monthly_rent = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Monthly rent in TZS'
    )
    locality = models.OneToOneField(Locality, on_delete=models.CASCADE, related_name='property')
    total_rooms = models.PositiveIntegerField(default=1)
    available_rooms = models.PositiveIntegerField(default=1)
    is_available = models.BooleanField(default=True)
    listed_date = models.DateField(auto_now_add=True)
    rules_terms = models.TextField(blank=True, help_text='Property rules and terms')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-listed_date']
    
    def __str__(self):
        return f"{self.title} - {self.locality}"
    
    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return sum(r.rating for r in reviews) / reviews.count()
        return None


class PropertyImage(models.Model):
    """Property images model."""
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
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
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='amenities')
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
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='units')
    unit_type = models.CharField(max_length=20, choices=UNIT_TYPE_CHOICES)
    unit_number = models.CharField(max_length=20)
    unit_rent = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text='Monthly rent for this unit in TZS'
    )
    area_sqm = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True,
        help_text='Area in square meters'
    )
    is_occupied = models.BooleanField(default=False)
    unit_features = models.TextField(blank=True, help_text='Specific features of this unit')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['property', 'unit_number']
        ordering = ['property', 'unit_number']
    
    def __str__(self):
        return f"{self.property.title} - Unit {self.unit_number}"
