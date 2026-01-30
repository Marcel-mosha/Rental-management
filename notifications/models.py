from django.db import models
from accounts.models import User


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
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    message_swahili = models.TextField(blank=True, help_text='Swahili translation')
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
