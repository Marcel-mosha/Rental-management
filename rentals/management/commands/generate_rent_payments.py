"""
Management command to generate rent payment records.
Should be run monthly to create payment records for active leases.

Usage:
    python manage.py generate_rent_payments --month 1 --year 2026
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date
from calendar import monthrange
from rentals.models import LeaseAgreement, Payment


class Command(BaseCommand):
    help = 'Generate rent payment records for active leases'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=int,
            help='Month to generate payments for (1-12)',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Year to generate payments for',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        today = timezone.now().date()
        
        # Determine target month/year
        month = options.get('month') or today.month
        year = options.get('year') or today.year
        
        self.stdout.write(f"Generating rent payments for {month}/{year}")
        
        # Get active leases
        active_leases = LeaseAgreement.objects.filter(status='active')
        
        created_count = 0
        skipped_count = 0
        
        for lease in active_leases:
            # Determine payment period string
            month_names = [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]
            payment_period = f"{month_names[month-1]} {year}"
            
            # Check if payment already exists for this period
            existing = Payment.objects.filter(
                lease=lease,
                payment_period=payment_period
            ).exists()
            
            if existing:
                skipped_count += 1
                self.stdout.write(
                    f"  Skipped (exists): {lease.tenant.user.get_full_name()} - "
                    f"{payment_period}"
                )
                continue
            
            # Calculate due date
            due_day = min(lease.payment_due_day, monthrange(year, month)[1])
            due_date = date(year, month, due_day)
            
            # Skip if due date is before lease start or after lease end
            if due_date < lease.start_date or due_date > lease.end_date:
                skipped_count += 1
                continue
            
            if not dry_run:
                Payment.objects.create(
                    lease=lease,
                    tenant=lease.tenant,
                    owner=lease.unit.property.owner,
                    amount=lease.monthly_rent,
                    payment_method='mpesa',  # Default
                    due_date=due_date,
                    payment_period=payment_period,
                    payment_status='pending'
                )
            
            created_count += 1
            self.stdout.write(
                f"  Created: {lease.tenant.user.get_full_name()} - "
                f"TZS {lease.monthly_rent} - Due: {due_date}"
            )
        
        # Summary
        self.stdout.write(self.style.SUCCESS(
            f"\nPayment generation completed:"
            f"\n  Created: {created_count}"
            f"\n  Skipped: {skipped_count}"
        ))
        
        if dry_run:
            self.stdout.write(self.style.WARNING("\nDry run - no payments created"))
