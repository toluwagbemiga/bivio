
# backend/apps/savings/admin.py
"""
Savings admin configuration
"""

from django.contrib import admin
from .models import SavingsAccount, SavingsTransaction, SavingsGoal


@admin.register(SavingsAccount)
class SavingsAccountAdmin(admin.ModelAdmin):
    list_display = ['account_number', 'user', 'account_name', 'account_type', 'current_balance', 'status', 'is_default']
    list_filter = ['account_type', 'status', 'is_default', 'auto_save_enabled']
    search_fields = ['account_number', 'account_name', 'user__email']
    readonly_fields = ['account_number', 'current_balance', 'total_interest_earned', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Account Information', {
            'fields': ('user', 'account_number', 'account_name', 'account_type', 'status', 'is_default')
        }),
        ('Balance', {
            'fields': ('current_balance', 'minimum_balance', 'target_amount')
        }),
        ('Auto-Save Settings', {
            'fields': ('auto_save_enabled', 'auto_save_percentage', 'auto_save_minimum', 'auto_save_maximum')
        }),
        ('Interest', {
            'fields': ('interest_rate', 'last_interest_calculation', 'total_interest_earned')
        }),
    )


@admin.register(SavingsTransaction)
class SavingsTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_reference', 'savings_account', 'transaction_type', 'amount', 'balance_after', 'status', 'transaction_date']
    list_filter = ['transaction_type', 'status', 'transaction_date']
    search_fields = ['transaction_reference', 'reference', 'source_transaction_id']
    readonly_fields = ['transaction_reference', 'balance_before', 'balance_after', 'transaction_date', 'created_at']


@admin.register(SavingsGoal)
class SavingsGoalAdmin(admin.ModelAdmin):
    list_display = ['name', 'savings_account', 'target_amount', 'current_amount', 'target_date', 'status']
    list_filter = ['status', 'target_date']
    search_fields = ['name', 'savings_account__account_name']
    readonly_fields = ['current_amount', 'monthly_target', 'completed_date', 'created_at', 'updated_at']


