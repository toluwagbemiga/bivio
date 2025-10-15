# backend/apps/transactions/admin.py
"""
Transaction admin configuration
"""

from django.contrib import admin
from .models import Transaction, TransactionItem


class TransactionItemInline(admin.TabularInline):
    model = TransactionItem
    extra = 0
    readonly_fields = ['line_total']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'user', 'transaction_type', 'total_amount', 'payment_method', 'status', 'transaction_date']
    list_filter = ['transaction_type', 'payment_method', 'status', 'transaction_date']
    search_fields = ['transaction_number', 'reference_number', 'user__email', 'customer_name', 'customer_phone']
    readonly_fields = ['transaction_number', 'transaction_date', 'updated_at']
    inlines = [TransactionItemInline]
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('user', 'transaction_number', 'reference_number', 'transaction_type', 'status')
        }),
        ('Financial Details', {
            'fields': ('subtotal', 'tax_amount', 'discount_amount', 'total_amount')
        }),
        ('Payment', {
            'fields': ('payment_method', 'amount_paid', 'change_amount')
        }),
        ('Customer', {
            'fields': ('customer_name', 'customer_phone', 'customer_email')
        }),
        ('AI & POS', {
            'fields': ('ai_category', 'ai_confidence', 'pos_device_serial', 'pos_transaction_id')
        }),
        ('Auto-Save', {
            'fields': ('auto_save_amount', 'auto_save_applied')
        }),
        ('Location', {
            'fields': ('latitude', 'longitude')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )




@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'get_product_name', 'quantity', 'unit_price', 'line_total']
    list_filter = ['transaction__transaction_date']
    search_fields = ['product__name', 'transaction__transaction_number']  # Changed from 'product_name'
    readonly_fields = ['line_total']
    
    def get_product_name(self, obj):
        """Display the product name from the related Product model"""
        return obj.product.name if obj.product else 'N/A'
    get_product_name.short_description = 'Product Name'
    get_product_name.admin_order_field = 'product__name'  # Allows sorting by product name