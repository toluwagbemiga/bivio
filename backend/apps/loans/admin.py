# backend/apps/loans/admin.py
"""
Loan admin configuration
"""

from django.contrib import admin
from .models import LoanProduct, Loan, LoanRepayment


@admin.register(LoanProduct)
class LoanProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'min_amount', 'max_amount', 'interest_rate', 'interest_type', 'repayment_frequency', 'is_active']
    list_filter = ['interest_type', 'repayment_frequency', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Loan)
class LoanAdmin(admin.ModelAdmin):
    list_display = ['loan_number', 'borrower', 'principal_amount', 'total_amount', 'outstanding_balance', 'status', 'risk_level', 'disbursed_date']
    list_filter = ['status', 'risk_level', 'collateral_type', 'disbursed_date']
    search_fields = ['loan_number', 'borrower__email', 'borrower__first_name', 'borrower__last_name']
    readonly_fields = ['loan_number', 'processing_fee', 'total_interest', 'total_amount', 'monthly_installment', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Loan Information', {
            'fields': ('borrower', 'loan_product', 'loan_number', 'status')
        }),
        ('Loan Terms', {
            'fields': ('principal_amount', 'interest_rate', 'tenure_days', 'processing_fee', 'total_interest', 'total_amount', 'monthly_installment')
        }),
        ('Repayment Tracking', {
            'fields': ('amount_paid', 'outstanding_balance', 'days_past_due', 'risk_level')
        }),
        ('Important Dates', {
            'fields': ('approved_date', 'disbursed_date', 'first_repayment_date', 'final_repayment_date')
        }),
        ('Collateral', {
            'fields': ('collateral_type', 'collateral_value', 'collateral_description')
        }),
        ('Application', {
            'fields': ('purpose', 'business_plan')
        }),
        ('Decision', {
            'fields': ('approved_by', 'approval_notes', 'rejection_reason')
        }),
        ('Auto-Deduction', {
            'fields': ('enable_auto_deduction', 'auto_deduction_percentage')
        }),
    )


@admin.register(LoanRepayment)
class LoanRepaymentAdmin(admin.ModelAdmin):
    list_display = ['payment_reference', 'loan', 'paid_amount', 'payment_method', 'payment_date', 'status', 'days_late']
    list_filter = ['repayment_type', 'payment_method', 'status', 'payment_date']
    search_fields = ['payment_reference', 'transaction_reference', 'loan__loan_number']
    readonly_fields = ['payment_reference', 'created_at', 'updated_at']

