# backend/apps/inventory/serializers.py
"""
Inventory serializers for products and categories
"""

from rest_framework import serializers
from .models import ProductCategory, Product, StockMovement


class ProductCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for product categories
    """
    product_count = serializers.ReadOnlyField(source='get_product_count')
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name', 'category_type', 'description', 'keywords',
            'local_names', 'is_active', 'product_count', 'created_at'
        ]
        read_only_fields = ['id', 'product_count', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for products with inventory tracking
    """
    profit_margin = serializers.ReadOnlyField()
    profit_per_unit = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    is_out_of_stock = serializers.ReadOnlyField()
    stock_status = serializers.ReadOnlyField()
    category_name = serializers.ReadOnlyField(source='category.name')
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'product_type', 'sku', 'barcode',
            'category', 'category_name', 'cost_price', 'selling_price',
            'current_stock', 'minimum_stock_level', 'maximum_stock_level',
            'unit_of_measurement', 'brand', 'manufacturer', 'expiry_date',
            'batch_number', 'local_names', 'supplier_name', 'supplier_phone',
            'total_sold', 'total_revenue', 'last_sold_date', 'last_restocked_date',
            'is_active', 'track_inventory', 'allow_negative_stock',
            'profit_margin', 'profit_per_unit', 'is_low_stock', 
            'is_out_of_stock', 'stock_status', 'created_at'
        ]
        read_only_fields = [
            'id', 'sku', 'total_sold', 'total_revenue', 'last_sold_date',
            'last_restocked_date', 'profit_margin', 'profit_per_unit',
            'is_low_stock', 'is_out_of_stock', 'stock_status', 'created_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class StockMovementSerializer(serializers.ModelSerializer):
    """
    Serializer for stock movements
    """
    product_name = serializers.ReadOnlyField(source='product.name')
    
    class Meta:
        model = StockMovement
        fields = [
            'id', 'product', 'product_name', 'movement_type', 'quantity',
            'unit_cost', 'stock_before', 'stock_after', 'reference_number',
            'notes', 'created_at'
        ]
        read_only_fields = ['id', 'product_name', 'created_at']


