"""
Management command to check and update lease statuses.
Should be run daily via cron job or scheduled task.

Usage:
    python manage.py check_lease_status
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from rentals.models import LeaseAgreement
from rentals.services import NotificationService


class Command(BaseCommand):
    help = 'Check and update lease statuses, send expiring notifications'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without actually doing it',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()
        
        self.stdout.write(f"Checking lease statuses for {today}")
        
        # Update expired leases
        expired_count = 0
        expired_leases = LeaseAgreement.objects.filter(
            status='active',
            end_date__lt=today
        )
        
        for lease in expired_leases:
            if not dry_run:
                lease.status = 'expired'
                lease.save()
            expired_count += 1
            self.stdout.write(
                f"  Expired: {lease.tenant.user.get_full_name()} - "
                f"{lease.unit.property.title}"
            )
        
        # Send expiring notifications (30 days, 14 days, 7 days)
        expiring_notifications = {
            30: 0,
            14: 0,
            7: 0,
        }
        
        for days in [30, 14, 7]:
            target_date = today + timedelta(days=days)
            expiring_leases = LeaseAgreement.objects.filter(
                status='active',
                end_date=target_date
            )
            
            for lease in expiring_leases:
                if not dry_run:
                    NotificationService.send_lease_expiring(lease, days)
                expiring_notifications[days] += 1
                self.stdout.write(
                    f"  Expiring in {days} days: {lease.tenant.user.get_full_name()} - "
                    f"{lease.unit.property.title}"
                )
        
        # Summary
        self.stdout.write(self.style.SUCCESS(
            f"\nLease status check completed:"
            f"\n  Marked as expired: {expired_count}"
            f"\n  Expiring in 30 days notifications: {expiring_notifications[30]}"
            f"\n  Expiring in 14 days notifications: {expiring_notifications[14]}"
            f"\n  Expiring in 7 days notifications: {expiring_notifications[7]}"
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nDry run - no changes made"))
