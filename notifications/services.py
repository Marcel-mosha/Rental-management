from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from .models import Notification


class NotificationService:
    """Service for handling notifications and emails."""
    
    @classmethod
    def create_notification(cls, user, notification_type, title, message, 
                           message_swahili='', action_url='', 
                           related_object_type='', related_object_id=None,
                           send_email=True):
        """Create a notification and optionally send an email."""
        
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            message_swahili=message_swahili,
            action_url=action_url,
            related_object_type=related_object_type,
            related_object_id=related_object_id
        )
        
        if send_email and user.email:
            cls.send_email_notification(notification)
        
        return notification
    
    @classmethod
    def send_email_notification(cls, notification):
        """Send email for a notification."""
        try:
            user = notification.user
            message = notification.get_message(user.preferred_language)
            
            send_mail(
                subject=notification.title,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True
            )
            
            notification.email_sent = True
            notification.email_sent_at = timezone.now()
            notification.save(update_fields=['email_sent', 'email_sent_at'])
            
        except Exception as e:
            # Log the error but don't fail
            print(f"Email sending failed: {e}")
    
    # ==================== Rent Reminder Notifications ====================
    
    @classmethod
    def send_rent_reminder_7_days(cls, payment):
        """Send rent reminder 7 days before due date."""
        user = payment.tenant.user
        
        message = (
            f"Reminder: Your rent payment of TZS {payment.amount:,.2f} for "
            f"{payment.payment_period} is due in 7 days on {payment.due_date}."
        )
        message_swahili = (
            f"Kumbusho: Malipo yako ya kodi ya TZS {payment.amount:,.2f} kwa "
            f"{payment.payment_period} yanakadhi kwa siku 7 tarehe {payment.due_date}."
        )
        
        return cls.create_notification(
            user=user,
            notification_type='rent_reminder_7',
            title='Rent Payment Reminder - 7 Days',
            message=message,
            message_swahili=message_swahili,
            action_url=f'/payments/{payment.id}',
            related_object_type='payment',
            related_object_id=payment.id
        )
    
    @classmethod
    def send_rent_reminder_3_days(cls, payment):
        """Send rent reminder 3 days before due date."""
        user = payment.tenant.user
        
        message = (
            f"Reminder: Your rent payment of TZS {payment.amount:,.2f} for "
            f"{payment.payment_period} is due in 3 days on {payment.due_date}."
        )
        message_swahili = (
            f"Kumbusho: Malipo yako ya kodi ya TZS {payment.amount:,.2f} kwa "
            f"{payment.payment_period} yanakadhi kwa siku 3 tarehe {payment.due_date}."
        )
        
        return cls.create_notification(
            user=user,
            notification_type='rent_reminder_3',
            title='Rent Payment Reminder - 3 Days',
            message=message,
            message_swahili=message_swahili,
            action_url=f'/payments/{payment.id}',
            related_object_type='payment',
            related_object_id=payment.id
        )
    
    @classmethod
    def send_rent_due_today(cls, payment):
        """Send notification on rent due date."""
        user = payment.tenant.user
        
        message = (
            f"Your rent payment of TZS {payment.amount:,.2f} for "
            f"{payment.payment_period} is due today."
        )
        message_swahili = (
            f"Malipo yako ya kodi ya TZS {payment.amount:,.2f} kwa "
            f"{payment.payment_period} yanakadhi leo."
        )
        
        return cls.create_notification(
            user=user,
            notification_type='rent_due',
            title='Rent Payment Due Today',
            message=message,
            message_swahili=message_swahili,
            action_url=f'/payments/{payment.id}',
            related_object_type='payment',
            related_object_id=payment.id
        )
    
    @classmethod
    def send_rent_overdue(cls, payment, days_overdue):
        """Send notification for overdue rent."""
        user = payment.tenant.user
        
        message = (
            f"Your rent payment of TZS {payment.amount:,.2f} for "
            f"{payment.payment_period} is {days_overdue} days overdue. "
            f"Please make your payment as soon as possible."
        )
        message_swahili = (
            f"Malipo yako ya kodi ya TZS {payment.amount:,.2f} kwa "
            f"{payment.payment_period} yamechelewa kwa siku {days_overdue}. "
            f"Tafadhali fanya malipo haraka iwezekanavyo."
        )
        
        return cls.create_notification(
            user=user,
            notification_type='rent_overdue',
            title=f'Rent Payment Overdue - {days_overdue} Days',
            message=message,
            message_swahili=message_swahili,
            action_url=f'/payments/{payment.id}',
            related_object_type='payment',
            related_object_id=payment.id
        )
    
    # ==================== Payment Notifications ====================
    
    @classmethod
    def send_payment_received(cls, payment):
        """Notify owner that a payment has been submitted."""
        user = payment.owner.user
        tenant_name = payment.tenant.user.get_full_name()
        
        message = (
            f"Payment of TZS {payment.amount:,.2f} has been submitted by "
            f"{tenant_name} for {payment.payment_period}. "
            f"Please verify this payment."
        )
        message_swahili = (
            f"Malipo ya TZS {payment.amount:,.2f} yamewasilishwa na "
            f"{tenant_name} kwa {payment.payment_period}. "
            f"Tafadhali thibitisha malipo haya."
        )
        
        return cls.create_notification(
            user=user,
            notification_type='payment_received',
            title='Payment Received - Verification Required',
            message=message,
            message_swahili=message_swahili,
            action_url=f'/payments/{payment.id}',
            related_object_type='payment',
            related_object_id=payment.id
        )
    
    @classmethod
    def send_payment_verified(cls, payment):
        """Notify tenant that payment has been verified."""
        user = payment.tenant.user
        
        message = (
            f"Your payment of TZS {payment.amount:,.2f} for {payment.payment_period} "
            f"has been verified and confirmed. Receipt number: {payment.receipt_number}"
        )
        message_swahili = (
            f"Malipo yako ya TZS {payment.amount:,.2f} kwa {payment.payment_period} "
            f"yamethibitishwa. Nambari ya risiti: {payment.receipt_number}"
        )
        
        return cls.create_notification(
            user=user,
            notification_type='payment_verified',
            title='Payment Verified',
            message=message,
            message_swahili=message_swahili,
            action_url=f'/payments/{payment.id}',
            related_object_type='payment',
            related_object_id=payment.id
        )
    
    @classmethod
    def send_payment_rejected(cls, payment):
        """Notify tenant that payment has been rejected."""
        user = payment.tenant.user
        
        message = (
            f"Your payment of TZS {payment.amount:,.2f} for {payment.payment_period} "
            f"could not be verified. Reason: {payment.notes}. "
            f"Please contact your landlord or resubmit the payment."
        )
        message_swahili = (
            f"Malipo yako ya TZS {payment.amount:,.2f} kwa {payment.payment_period} "
            f"hayakuweza kuthibitishwa. Sababu: {payment.notes}. "
            f"Tafadhali wasiliana na mmiliki wako au wasilisha tena malipo."
        )
        
        return cls.create_notification(
            user=user,
            notification_type='payment_rejected',
            title='Payment Verification Failed',
            message=message,
            message_swahili=message_swahili,
            action_url=f'/payments/{payment.id}',
            related_object_type='payment',
            related_object_id=payment.id
        )
    
    # ==================== Lease Notifications ====================
    
    @classmethod
    def send_lease_created(cls, lease):
        """Notify both parties about new lease."""
        unit = lease.unit
        property_obj = unit.property
        
        # Notify tenant
        tenant_message = (
            f"A new lease agreement has been created for {property_obj.title}, "
            f"Unit {unit.unit_number}. Please review and sign the agreement."
        )
        tenant_message_sw = (
            f"Mkataba mpya wa kukodisha umeundwa kwa {property_obj.title}, "
            f"Chumba {unit.unit_number}. Tafadhali soma na saini mkataba."
        )
        
        cls.create_notification(
            user=lease.tenant.user,
            notification_type='lease_created',
            title='New Lease Agreement Created',
            message=tenant_message,
            message_swahili=tenant_message_sw,
            action_url=f'/leases/{lease.id}',
            related_object_type='lease',
            related_object_id=lease.id
        )
        
        # Notify owner
        owner_message = (
            f"A new lease agreement has been created with "
            f"{lease.tenant.user.get_full_name()} for {property_obj.title}, "
            f"Unit {unit.unit_number}."
        )
        
        return cls.create_notification(
            user=property_obj.owner.user,
            notification_type='lease_created',
            title='New Lease Agreement Created',
            message=owner_message,
            action_url=f'/leases/{lease.id}',
            related_object_type='lease',
            related_object_id=lease.id
        )
    
    @classmethod
    def send_lease_expiring(cls, lease, days_until_expiry):
        """Notify about expiring lease."""
        # Notify tenant
        tenant_message = (
            f"Your lease for {lease.unit.property.title}, Unit {lease.unit.unit_number} "
            f"will expire in {days_until_expiry} days on {lease.end_date}. "
            f"Please contact your landlord about renewal."
        )
        tenant_message_sw = (
            f"Mkataba wako wa {lease.unit.property.title}, Chumba {lease.unit.unit_number} "
            f"utaisha kwa siku {days_until_expiry} tarehe {lease.end_date}. "
            f"Tafadhali wasiliana na mmiliki wako kuhusu kuhuisha."
        )
        
        cls.create_notification(
            user=lease.tenant.user,
            notification_type='lease_expiring',
            title=f'Lease Expiring in {days_until_expiry} Days',
            message=tenant_message,
            message_swahili=tenant_message_sw,
            action_url=f'/leases/{lease.id}',
            related_object_type='lease',
            related_object_id=lease.id
        )
        
        # Notify owner
        owner_message = (
            f"The lease with {lease.tenant.user.get_full_name()} for "
            f"{lease.unit.property.title}, Unit {lease.unit.unit_number} "
            f"will expire in {days_until_expiry} days on {lease.end_date}."
        )
        
        return cls.create_notification(
            user=lease.unit.property.owner.user,
            notification_type='lease_expiring',
            title=f'Lease Expiring in {days_until_expiry} Days',
            message=owner_message,
            action_url=f'/leases/{lease.id}',
            related_object_type='lease',
            related_object_id=lease.id
        )
    
    @classmethod
    def send_lease_renewed(cls, lease):
        """Notify about renewed lease."""
        tenant_message = (
            f"Your lease for {lease.unit.property.title}, Unit {lease.unit.unit_number} "
            f"has been renewed. New term: {lease.start_date} to {lease.end_date}. "
            f"Monthly rent: TZS {lease.monthly_rent:,.2f}"
        )
        
        return cls.create_notification(
            user=lease.tenant.user,
            notification_type='lease_renewed',
            title='Lease Renewed',
            message=tenant_message,
            action_url=f'/leases/{lease.id}',
            related_object_type='lease',
            related_object_id=lease.id
        )
    
    # ==================== Maintenance Notifications ====================
    
    @classmethod
    def send_maintenance_submitted(cls, request):
        """Notify owner about new maintenance request."""
        user = request.owner.user
        tenant_name = request.tenant.user.get_full_name()
        
        message = (
            f"New maintenance request from {tenant_name} for "
            f"{request.unit.property.title}, Unit {request.unit.unit_number}. "
            f"Issue: {request.get_issue_type_display()}. "
            f"Priority: {request.get_priority_display()}."
        )
        
        return cls.create_notification(
            user=user,
            notification_type='maintenance_submitted',
            title='New Maintenance Request',
            message=message,
            action_url=f'/maintenance/{request.id}',
            related_object_type='maintenance',
            related_object_id=request.id
        )
    
    @classmethod
    def send_maintenance_update(cls, request, new_status):
        """Notify tenant about maintenance status update."""
        user = request.tenant.user
        
        status_messages = {
            'acknowledged': 'Your maintenance request has been acknowledged.',
            'in_progress': 'Work on your maintenance request has started.',
            'completed': f'Your maintenance request has been completed. '
                        f'Cost: TZS {request.cost:,.2f}' if request.cost else 
                        'Your maintenance request has been completed.',
            'cancelled': 'Your maintenance request has been cancelled.'
        }
        
        status_messages_sw = {
            'acknowledged': 'Ombi lako la matengenezo limekubaliwa.',
            'in_progress': 'Kazi ya matengenezo yako imeanza.',
            'completed': 'Matengenezo yako yamekamilika.',
            'cancelled': 'Ombi lako la matengenezo limefutwa.'
        }
        
        message = status_messages.get(new_status, f'Status updated to: {new_status}')
        message_sw = status_messages_sw.get(new_status, '')
        
        notification_type = f'maintenance_{new_status}'
        if notification_type not in dict(Notification.NOTIFICATION_TYPE_CHOICES):
            notification_type = 'maintenance_in_progress'
        
        return cls.create_notification(
            user=user,
            notification_type=notification_type,
            title=f'Maintenance Request Update: {new_status.replace("_", " ").title()}',
            message=message,
            message_swahili=message_sw,
            action_url=f'/maintenance/{request.id}',
            related_object_type='maintenance',
            related_object_id=request.id
        )
    
    # ==================== Review Notifications ====================
    
    @classmethod
    def send_new_review(cls, review):
        """Notify about new review."""
        if review.review_type == 'tenant_to_property':
            # Notify property owner
            user = review.property.owner.user
            message = (
                f"Your property {review.property.title} has received a new "
                f"{review.rating}-star review from {review.reviewer.get_full_name()}."
            )
        else:
            # Notify tenant
            user = review.tenant.user
            message = (
                f"You have received a new {review.rating}-star review from "
                f"your landlord {review.reviewer.get_full_name()}."
            )
        
        return cls.create_notification(
            user=user,
            notification_type='new_review',
            title='New Review Received',
            message=message,
            action_url=f'/reviews/{review.id}',
            related_object_type='review',
            related_object_id=review.id
        )
    
    @classmethod
    def send_review_response(cls, review):
        """Notify about review response."""
        # Notify the original reviewer
        message = (
            f"Your review has received a response from "
            f"{review.response_by.get_full_name()}."
        )
        
        return cls.create_notification(
            user=review.reviewer,
            notification_type='review_response',
            title='Response to Your Review',
            message=message,
            action_url=f'/reviews/{review.id}',
            related_object_type='review',
            related_object_id=review.id
        )
    
    # ==================== Account Notifications ====================
    
    @classmethod
    def send_account_verified(cls, user):
        """Notify user that their account has been verified."""
        message = (
            "Congratulations! Your account has been verified. "
            "You now have full access to all features."
        )
        message_sw = (
            "Hongera! Akaunti yako imethibitishwa. "
            "Sasa una ufikiaji kamili wa vipengele vyote."
        )
        
        return cls.create_notification(
            user=user,
            notification_type='account_verified',
            title='Account Verified',
            message=message,
            message_swahili=message_sw,
            action_url='/profile'
        )
    
    @classmethod
    def send_document_verified(cls, document):
        """Notify user that their document has been verified."""
        user = document.user
        
        message = (
            f"Your {document.get_document_type_display()} has been verified."
        )
        message_sw = (
            f"{document.get_document_type_display()} yako imethibitishwa."
        )
        
        return cls.create_notification(
            user=user,
            notification_type='document_verified',
            title='Document Verified',
            message=message,
            message_swahili=message_sw,
            action_url='/documents',
            related_object_type='document',
            related_object_id=document.id
        )
