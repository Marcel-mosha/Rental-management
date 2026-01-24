from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import (
    User, Document, Tenant, Owner, Location, Property, PropertyImage,
    PropertyAmenity, RentalUnit, LeaseAgreement, Payment,
    MaintenanceRequest, MaintenanceImage, Review, Notification
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin configuration for custom User model."""
    
    list_display = ['username', 'email', 'first_name', 'last_name', 
                    'user_type', 'phone_number', 'is_verified', 'is_active']
    list_filter = ['user_type', 'is_verified', 'is_active', 'is_staff', 
                   'preferred_language', 'registration_date']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Additional Info'), {
            'fields': ('user_type', 'phone_number', 'profile_image', 
                      'is_verified', 'verification_document', 'preferred_language')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Additional Info'), {
            'fields': ('user_type', 'phone_number', 'preferred_language')
        }),
    )
    
    actions = ['verify_users', 'unverify_users']
    
    @admin.action(description='Verify selected users')
    def verify_users(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f'{count} users verified successfully.')
    
    @admin.action(description='Unverify selected users')
    def unverify_users(self, request, queryset):
        count = queryset.update(is_verified=False)
        self.message_user(request, f'{count} users unverified.')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin configuration for Document model."""
    
    list_display = ['user', 'document_type', 'upload_date', 'is_verified']
    list_filter = ['document_type', 'is_verified', 'upload_date']
    search_fields = ['user__username', 'user__first_name', 'user__last_name']
    ordering = ['-upload_date']
    readonly_fields = ['upload_date']
    
    actions = ['verify_documents']
    
    @admin.action(description='Verify selected documents')
    def verify_documents(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(request, f'{count} documents verified.')


@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    """Admin configuration for Tenant model."""
    
    list_display = ['get_full_name', 'get_email', 'get_phone', 'occupation', 
                    'employer_name', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 
                     'occupation', 'employer_name']
    ordering = ['-created_at']
    raw_id_fields = ['user']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    
    def get_phone(self, obj):
        return obj.user.phone_number
    get_phone.short_description = 'Phone'


@admin.register(Owner)
class OwnerAdmin(admin.ModelAdmin):
    """Admin configuration for Owner model."""
    
    list_display = ['get_full_name', 'get_email', 'company_name', 
                    'total_properties', 'total_earnings', 'created_at']
    list_filter = ['bank_name', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email',
                     'company_name', 'tax_identification_number']
    ordering = ['-created_at']
    raw_id_fields = ['user']
    readonly_fields = ['total_properties', 'total_earnings']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()
    get_full_name.short_description = 'Full Name'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin configuration for Location model."""
    
    list_display = ['street_address', 'ward', 'district', 'region', 'landmark']
    list_filter = ['region', 'district']
    search_fields = ['street_address', 'ward', 'district', 'landmark']
    ordering = ['region', 'district', 'ward']


class PropertyImageInline(admin.TabularInline):
    """Inline admin for PropertyImage."""
    model = PropertyImage
    extra = 1


class PropertyAmenityInline(admin.TabularInline):
    """Inline admin for PropertyAmenity."""
    model = PropertyAmenity
    extra = 1


class RentalUnitInline(admin.TabularInline):
    """Inline admin for RentalUnit."""
    model = RentalUnit
    extra = 1
    fields = ['unit_number', 'unit_type', 'unit_rent', 'is_occupied']


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Admin configuration for Property model."""
    
    list_display = ['title', 'property_type', 'get_owner_name', 'get_location',
                    'monthly_rent', 'available_rooms', 'total_rooms', 
                    'is_available', 'listed_date']
    list_filter = ['property_type', 'is_available', 'location__region', 
                   'location__district', 'listed_date']
    search_fields = ['title', 'description', 'owner__user__first_name',
                     'owner__user__last_name', 'location__street_address']
    ordering = ['-listed_date']
    raw_id_fields = ['owner', 'location']
    readonly_fields = ['listed_date', 'created_at', 'updated_at']
    inlines = [RentalUnitInline, PropertyImageInline, PropertyAmenityInline]
    
    def get_owner_name(self, obj):
        return obj.owner.user.get_full_name()
    get_owner_name.short_description = 'Owner'
    
    def get_location(self, obj):
        return f"{obj.location.district}, {obj.location.get_region_display()}"
    get_location.short_description = 'Location'


@admin.register(RentalUnit)
class RentalUnitAdmin(admin.ModelAdmin):
    """Admin configuration for RentalUnit model."""
    
    list_display = ['get_property_title', 'unit_number', 'unit_type', 
                    'unit_rent', 'is_occupied']
    list_filter = ['unit_type', 'is_occupied', 'property__location__region']
    search_fields = ['unit_number', 'property__title']
    ordering = ['property', 'unit_number']
    raw_id_fields = ['property']
    
    def get_property_title(self, obj):
        return obj.property.title
    get_property_title.short_description = 'Property'


@admin.register(LeaseAgreement)
class LeaseAgreementAdmin(admin.ModelAdmin):
    """Admin configuration for LeaseAgreement model."""
    
    list_display = ['get_tenant_name', 'get_property', 'get_unit', 
                    'start_date', 'end_date', 'monthly_rent', 'status']
    list_filter = ['status', 'payment_frequency', 'deposit_paid', 
                   'start_date', 'end_date']
    search_fields = ['tenant__user__first_name', 'tenant__user__last_name',
                     'unit__property__title', 'unit__unit_number']
    ordering = ['-start_date']
    raw_id_fields = ['tenant', 'unit']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'start_date'
    
    def get_tenant_name(self, obj):
        return obj.tenant.user.get_full_name()
    get_tenant_name.short_description = 'Tenant'
    
    def get_property(self, obj):
        return obj.unit.property.title
    get_property.short_description = 'Property'
    
    def get_unit(self, obj):
        return obj.unit.unit_number
    get_unit.short_description = 'Unit'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """Admin configuration for Payment model."""
    
    list_display = ['get_tenant_name', 'amount', 'payment_method', 
                    'payment_status', 'due_date', 'payment_date', 
                    'receipt_number', 'is_late']
    list_filter = ['payment_status', 'payment_method', 'due_date', 
                   'payment_date', 'created_at']
    search_fields = ['tenant__user__first_name', 'tenant__user__last_name',
                     'transaction_id', 'mobile_money_code', 'receipt_number']
    ordering = ['-due_date']
    raw_id_fields = ['lease', 'tenant', 'owner', 'verified_by']
    readonly_fields = ['receipt_number', 'verified_at', 'created_at', 'updated_at']
    date_hierarchy = 'due_date'
    
    actions = ['verify_payments', 'reject_payments']
    
    def get_tenant_name(self, obj):
        return obj.tenant.user.get_full_name()
    get_tenant_name.short_description = 'Tenant'
    
    @admin.action(description='Verify selected payments')
    def verify_payments(self, request, queryset):
        from django.utils import timezone
        for payment in queryset.filter(payment_status='pending_verification'):
            payment.payment_status = 'completed'
            payment.verified_by = request.user
            payment.verified_at = timezone.now()
            if not payment.payment_date:
                payment.payment_date = timezone.now().date()
            payment.generate_receipt_number()
            payment.save()
        self.message_user(request, 'Payments verified successfully.')
    
    @admin.action(description='Reject selected payments')
    def reject_payments(self, request, queryset):
        count = queryset.filter(payment_status='pending_verification').update(
            payment_status='failed'
        )
        self.message_user(request, f'{count} payments rejected.')


class MaintenanceImageInline(admin.TabularInline):
    """Inline admin for MaintenanceImage."""
    model = MaintenanceImage
    extra = 1


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    """Admin configuration for MaintenanceRequest model."""
    
    list_display = ['get_tenant_name', 'get_property', 'issue_type', 
                    'priority', 'status', 'request_date', 'cost']
    list_filter = ['status', 'priority', 'issue_type', 'cost_responsibility',
                   'request_date']
    search_fields = ['tenant__user__first_name', 'tenant__user__last_name',
                     'unit__property__title', 'description', 'technician_name']
    ordering = ['-request_date']
    raw_id_fields = ['tenant', 'unit', 'owner']
    readonly_fields = ['request_date']
    inlines = [MaintenanceImageInline]
    
    def get_tenant_name(self, obj):
        return obj.tenant.user.get_full_name()
    get_tenant_name.short_description = 'Tenant'
    
    def get_property(self, obj):
        return obj.unit.property.title
    get_property.short_description = 'Property'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Admin configuration for Review model."""
    
    list_display = ['get_reviewer_name', 'review_type', 'rating', 
                    'review_date', 'is_visible']
    list_filter = ['review_type', 'rating', 'is_visible', 'review_date']
    search_fields = ['reviewer__first_name', 'reviewer__last_name',
                     'comment', 'response']
    ordering = ['-review_date']
    raw_id_fields = ['reviewer', 'tenant', 'property', 'lease', 'response_by']
    readonly_fields = ['review_date', 'response_date']
    
    def get_reviewer_name(self, obj):
        return obj.reviewer.get_full_name()
    get_reviewer_name.short_description = 'Reviewer'


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin configuration for Notification model."""
    
    list_display = ['get_user_name', 'notification_type', 'title', 
                    'is_read', 'email_sent', 'created_at']
    list_filter = ['notification_type', 'is_read', 'email_sent', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'title', 'message']
    ordering = ['-created_at']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'email_sent_at']
    
    def get_user_name(self, obj):
        return obj.user.get_full_name()
    get_user_name.short_description = 'User'
