from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, Tenant
from properties.models import Property
from leases.models import LeaseAgreement


class Review(models.Model):
    """Review model for two-way rating system."""
    
    REVIEW_TYPE_CHOICES = [
        ('tenant_to_property', 'Tenant reviewing Property'),
        ('owner_to_tenant', 'Owner reviewing Tenant'),
    ]
    
    review_type = models.CharField(max_length=30, choices=REVIEW_TYPE_CHOICES)
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews_written')
    tenant = models.ForeignKey(
        Tenant, on_delete=models.CASCADE, related_name='reviews_received',
        null=True, blank=True, help_text='For owner reviewing tenant'
    )
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='reviews',
        null=True, blank=True, help_text='For tenant reviewing property'
    )
    lease = models.ForeignKey(
        LeaseAgreement, on_delete=models.CASCADE, related_name='reviews',
        help_text='Verified lease for this review'
    )
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)
    response = models.TextField(blank=True)
    response_date = models.DateTimeField(null=True, blank=True)
    response_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='review_responses'
    )
    is_visible = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-review_date']
    
    def __str__(self):
        return f"Review by {self.reviewer.get_full_name()} - {self.rating} stars"
