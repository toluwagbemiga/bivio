# backend/apps/inventory/models.py
"""
Inventory management models for POS Financial Management App
Handles products, categories, and stock management
"""

import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class ProductCategory(models.Model):
    """
    Product categories with Nigerian market focus
    """
    
    CATEGORY_TYPES = [
        ('food_beverages', 'Food & Beverages'),
        ('electronics', 'Electronics'),
        ('clothing', 'Clothing & Fashion'),
        ('household', 'Household Items'),
        ('cosmetics', 'Cosmetics & Personal Care'),
        ('stationery', 'Stationery & Office'),
        ('pharmacy', 'Pharmacy & Health'),
        ('services', 'Services'),
        ('airtime_data', 'Airtime & Data'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    
    # AI Training features
    keywords = models.TextField(
        blank=True,
        help_text='Comma-separated keywords for AI categorization'
    )
    local_names = models.TextField(
        blank=True,
        help_text='Local/Pidgin names for products in this category'
    )
    
    # Business metrics
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_categories'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'product_categories'
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        ordering = ['name']
        indexes = [
            models.Index(fields=['category_type']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_product_count(self):
        """Get number of products in this category"""
        return self.products.filter(is_active=True).count()


class Product(models.Model):
    """
    Product model with Nigerian context
    Supports both retail and service products
    """
    
    PRODUCT_TYPES = [
        ('goods', 'Physical Goods'),
        ('services', 'Services'),
        ('digital', 'Digital Products'),
    ]
    
    UNITS = [
        ('pieces', 'Pieces'),
        ('kg', 'Kilograms'),
        ('liters', 'Liters'),
        ('meters', 'Meters'),
        ('packs', 'Packs'),
        ('cartons', 'Cartons'),
        ('bottles', 'Bottles'),
        ('bags', 'Bags'),
        ('rolls', 'Rolls'),
        ('hours', 'Hours'),
        ('days', 'Days'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='products'
    )
    category = models.ForeignKey(
        ProductCategory,
        on_delete=models.PROTECT,
        related_name='products'
    )
    
    # Product Information
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='goods')
    
    # SKU and Identification
    sku = models.CharField(
        max_length=100,
        blank=True,
        help_text='Stock Keeping Unit - auto-generated if empty'
    )
    barcode = models.CharField(max_length=100, blank=True, null=True)
    
    # Pricing
    cost_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Cost price per unit in Naira'
    )
    selling_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Selling price per unit in Naira'
    )
    
    # Inventory
    current_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    minimum_stock_level = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Alert when stock falls below this level'
    )
    maximum_stock_level = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Maximum stock to maintain'
    )
    unit_of_measurement = models.CharField(max_length=20, choices=UNITS, default='pieces')
    
    # Product Features
    brand = models.CharField(max_length=100, blank=True)
    manufacturer = models.CharField(max_length=200, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    batch_number = models.CharField(max_length=100, blank=True)
    
    # Nigerian-specific
    local_names = models.TextField(
        blank=True,
        help_text='Local names for this product (Hausa, Igbo, Yoruba, Pidgin)'
    )
    supplier_name = models.CharField(max_length=200, blank=True)
    supplier_phone = models.CharField(max_length=15, blank=True)
    
    # Business Analytics
    total_sold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Total quantity sold'
    )
    total_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Total revenue generated from this product'
    )
    last_sold_date = models.DateTimeField(null=True, blank=True)
    last_restocked_date = models.DateTimeField(null=True, blank=True)
    
    # Status and Settings
    is_active = models.BooleanField(default=True)
    track_inventory = models.BooleanField(
        default=True,
        help_text='Whether to track inventory for this product'
    )
    allow_negative_stock = models.BooleanField(
        default=False,
        help_text='Allow sales even when stock is zero'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        unique_together = ['user', 'sku']
        ordering = ['name']
        indexes = [
            models.Index(fields=['user', 'category']),
            models.Index(fields=['sku']),
            models.Index(fields=['barcode']),
            models.Index(fields=['is_active']),
            models.Index(fields=['current_stock']),
            models.Index(fields=['minimum_stock_level']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.business_profile.business_name if hasattr(self.user, 'business_profile') else self.user.username}"
    
    def save(self, *args, **kwargs):
        """Auto-generate SKU if not provided"""
        if not self.sku:
            # Generate SKU: Category-UserID-ProductCounter
            user_product_count = Product.objects.filter(user=self.user).count() + 1
            category_code = self.category.category_type[:3].upper()
            user_code = str(self.user.id)[:8].upper()
            self.sku = f"{category_code}-{user_code}-{user_product_count:03d}"
        super().save(*args, **kwargs)
    
    @property
    def profit_margin(self):
        """Calculate profit margin percentage"""
        if self.cost_price > 0:
            return ((self.selling_price - self.cost_price) / self.cost_price) * 100
        return 0
    
    @property
    def profit_per_unit(self):
        """Calculate profit per unit"""
        return self.selling_price - self.cost_price
    
    @property
    def is_low_stock(self):
        """Check if product is below minimum stock level"""
        return self.current_stock <= self.minimum_stock_level
    
    @property
    def is_out_of_stock(self):
        """Check if product is out of stock"""
        return self.current_stock <= 0
    
    @property
    def stock_status(self):
        """Get stock status as string"""
        if self.is_out_of_stock:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        else:
            return 'in_stock'
    
    def can_sell(self, quantity):
        """Check if we can sell the specified quantity"""
        if not self.track_inventory:
            return True
        if self.allow_negative_stock:
            return True
        return self.current_stock >= quantity
    
    def update_stock(self, quantity_change, operation='add'):
        """Update stock level"""
        if operation == 'add':
            self.current_stock += quantity_change
            self.last_restocked_date = models.DateTimeField(auto_now=True)
        elif operation == 'subtract':
            self.current_stock -= quantity_change
            self.last_sold_date = models.DateTimeField(auto_now=True)
        self.save()


class StockMovement(models.Model):
    """
    Track all stock movements for audit and analytics
    """
    
    MOVEMENT_TYPES = [
        ('purchase', 'Purchase/Restock'),
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('adjustment', 'Stock Adjustment'),
        ('damage', 'Damage/Loss'),
        ('transfer', 'Transfer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_movements'
    )
    
    # Movement Details
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Cost per unit for this movement'
    )
    
    # Stock Levels
    stock_before = models.DecimalField(max_digits=10, decimal_places=2)
    stock_after = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Reference Information
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    # User who made the movement
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='stock_movements'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'stock_movements'
        verbose_name = _('Stock Movement')
        verbose_name_plural = _('Stock Movements')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product', 'movement_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"{self.movement_type.title()} - {self.product.name} - {self.quantity}"


