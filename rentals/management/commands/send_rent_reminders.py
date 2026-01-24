"""
Management command to send rent payment reminders.
Should be run daily via cron job or scheduled task.

Usage:
    python manage.py send_rent_reminders
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from rentals.models import Payment, LeaseAgreement
from rentals.services import NotificationService


class Command(BaseCommand):
    help = 'Send rent payment reminders (7 days, 3 days, due today, overdue)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()
        
        self.stdout.write(f"Processing rent reminders for {today}")
        
        # Get active leases
        active_leases = LeaseAgreement.objects.filter(status='active')
        
        reminders_sent = {
            '7_days': 0,
            '3_days': 0,
            'due_today': 0,
            'overdue': 0,
        }
        
        for lease in active_leases:
            # Get pending payments for this lease
            pending_payments = Payment.objects.filter(
                lease=lease,
                payment_status='pending'
            )
            
            for payment in pending_payments:
                days_until_due = (payment.due_date - today).days
                
                if days_until_due == 7:
                    # 7-day reminder
                    if not dry_run:
                        NotificationService.send_rent_reminder_7_days(payment)
                    reminders_sent['7_days'] += 1
                    self.stdout.write(
                        f"  7-day reminder: {payment.tenant.user.get_full_name()} - "
                        f"TZS {payment.amount}"
                    )
                
                elif days_until_due == 3:
                    # 3-day reminder
                    if not dry_run:
                        NotificationService.send_rent_reminder_3_days(payment)
                    reminders_sent['3_days'] += 1
                    self.stdout.write(
                        f"  3-day reminder: {payment.tenant.user.get_full_name()} - "
                        f"TZS {payment.amount}"
                    )
                
                elif days_until_due == 0:
                    # Due today
                    if not dry_run:
                        NotificationService.send_rent_due_today(payment)
                    reminders_sent['due_today'] += 1
                    self.stdout.write(
                        f"  Due today: {payment.tenant.user.get_full_name()} - "
                        f"TZS {payment.amount}"
                    )
                
                elif days_until_due < 0:
                    # Overdue
                    days_overdue = abs(days_until_due)
                    # Send overdue reminders every 3 days
                    if days_overdue % 3 == 0:
                        if not dry_run:
                            NotificationService.send_rent_overdue(payment, days_overdue)
                        reminders_sent['overdue'] += 1
                        self.stdout.write(
                            f"  Overdue ({days_overdue} days): "
                            f"{payment.tenant.user.get_full_name()} - TZS {payment.amount}"
                        )
        
        # Summary
        self.stdout.write(self.style.SUCCESS(
            f"\nReminders sent:"
            f"\n  7-day: {reminders_sent['7_days']}"
            f"\n  3-day: {reminders_sent['3_days']}"
            f"\n  Due today: {reminders_sent['due_today']}"
            f"\n  Overdue: {reminders_sent['overdue']}"
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nDry run - no notifications sent"))
