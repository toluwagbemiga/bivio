# backend/apps/users/admin.py
"""
User admin configuration
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, BusinessProfile, Guarantor


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'first_name', 'last_name', 'user_type', 'verification_status', 'is_active']
    list_filter = ['user_type', 'verification_status', 'is_active', 'created_at']
    search_fields = ['email', 'username', 'first_name', 'last_name', 'phone_number', 'bvn']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Nigerian ID', {'fields': ('bvn', 'nin')}),
        ('Account Type', {'fields': ('user_type', 'verification_status')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']


@admin.register(BusinessProfile)
class BusinessProfileAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'business_type', 'state', 'credit_score', 'risk_level', 'is_business_verified']
    list_filter = ['business_type', 'business_size', 'risk_level', 'is_business_verified', 'state']
    search_fields = ['business_name', 'user__email', 'business_registration_number', 'pos_device_serial']
    readonly_fields = ['credit_score', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Business Information', {
            'fields': ('user', 'business_name', 'business_type', 'business_size', 'business_description')
        }),
        ('Location', {
            'fields': ('business_address', 'state', 'lga', 'city')
        }),
        ('Financial Information', {
            'fields': ('estimated_monthly_revenue', 'years_in_business')
        }),
        ('Documentation', {
            'fields': ('business_registration_number', 'tax_identification_number')
        }),
        ('POS Information', {
            'fields': ('pos_device_serial', 'pos_provider')
        }),
        ('Credit & Risk', {
            'fields': ('credit_score', 'risk_level')
        }),
        ('Bank Details', {
            'fields': ('bank_account_number', 'bank_name', 'bank_code', 'account_name')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship')
        }),
        ('Verification', {
            'fields': ('is_business_verified', 'verification_documents_uploaded', 'kyc_completed')
        }),
    )


@admin.register(Guarantor)
class GuarantorAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'borrower', 'phone_number', 'relationship_to_borrower', 'is_verified', 'has_agreed_to_guarantee']
    list_filter = ['relationship_to_borrower', 'is_verified', 'has_agreed_to_guarantee']
    search_fields = ['full_name', 'phone_number', 'bvn', 'borrower__email']
    readonly_fields = ['created_at', 'updated_at', 'agreement_signed_at']


