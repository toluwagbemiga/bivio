# backend/apps/inventory/admin.py
"""
Inventory admin configuration
"""

from django.contrib import admin
from .models import ProductCategory, Product, StockMovement


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active']
    search_fields = ['name', 'keywords', 'local_names']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'category', 'sku', 'selling_price', 'current_stock', 'stock_status', 'is_active']
    list_filter = ['category', 'product_type', 'is_active', 'track_inventory']
    search_fields = ['name', 'sku', 'barcode', 'user__email', 'local_names']
    readonly_fields = ['sku', 'total_sold', 'total_revenue', 'last_sold_date', 'last_restocked_date', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'category', 'name', 'description', 'product_type')
        }),
        ('Identification', {
            'fields': ('sku', 'barcode')
        }),
        ('Pricing', {
            'fields': ('cost_price', 'selling_price')
        }),
        ('Inventory', {
            'fields': ('current_stock', 'minimum_stock_level', 'maximum_stock_level', 'unit_of_measurement')
        }),
        ('Product Details', {
            'fields': ('brand', 'manufacturer', 'expiry_date', 'batch_number', 'local_names')
        }),
        ('Supplier', {
            'fields': ('supplier_name', 'supplier_phone')
        }),
        ('Analytics', {
            'fields': ('total_sold', 'total_revenue', 'last_sold_date', 'last_restocked_date')
        }),
        ('Settings', {
            'fields': ('is_active', 'track_inventory', 'allow_negative_stock')
        }),
    )


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ['product', 'movement_type', 'quantity', 'stock_before', 'stock_after', 'created_at']
    list_filter = ['movement_type', 'created_at']
    search_fields = ['product__name', 'reference_number']
    readonly_fields = ['created_at']


