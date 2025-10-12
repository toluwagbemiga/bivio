# backend/apps/transactions/serializers.py
"""
Transaction serializers for POS sales and payments
"""

from rest_framework import serializers
from decimal import Decimal
from .models import Transaction, TransactionItem, TransactionCategory
from apps.inventory.models import Product


class TransactionCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for transaction categories
    """
    transaction_count = serializers.ReadOnlyField(source='get_transaction_count')
    
    class Meta:
        model = TransactionCategory
        fields = [
            'id', 'name', 'category_type', 'description', 'remark_keywords',
            'is_active', 'transaction_count', 'created_at'
        ]
        read_only_fields = ['id', 'transaction_count', 'created_at']


class TransactionItemSerializer(serializers.ModelSerializer):
    """
    Serializer for transaction items
    """
    product_name = serializers.ReadOnlyField()
    profit = serializers.ReadOnlyField()
    
    class Meta:
        model = TransactionItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'unit_price',
            'unit_cost', 'line_total', 'discount_amount', 'profit'
        ]
        read_only_fields = ['id', 'product_name', 'line_total', 'profit']


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for POS transactions
    """
    transaction_items = TransactionItemSerializer(many=True, read_only=True)
    profit = serializers.ReadOnlyField()
    is_paid = serializers.ReadOnlyField()
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'transaction_number', 'reference_number', 'transaction_type',
            'subtotal', 'tax_amount', 'discount_amount', 'total_amount',
            'payment_method', 'amount_paid', 'change_amount',
            'customer_name', 'customer_phone', 'customer_email',
            'status', 'notes', 'ai_category', 'ai_confidence',
            'pos_device_serial', 'pos_transaction_id', 'latitude', 'longitude',
            'auto_save_amount', 'auto_save_applied', 'transaction_date',
            'transaction_items', 'profit', 'is_paid'
        ]
        read_only_fields = [
            'id', 'transaction_number', 'transaction_items', 'profit', 
            'is_paid', 'transaction_date'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new transactions with items
    """
    items = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        help_text="List of transaction items"
    )
    
    class Meta:
        model = Transaction
        fields = [
            'transaction_type', 'payment_method', 'customer_name',
            'customer_phone', 'customer_email', 'notes',
            'pos_device_serial', 'pos_transaction_id', 'items'
        ]
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data['user'] = self.context['request'].user
        
        # Calculate totals
        subtotal = Decimal('0.00')
        total_cost = Decimal('0.00')
        
        # Validate items and calculate totals
        for item_data in items_data:
            try:
                product = Product.objects.get(
                    id=item_data['product_id'], 
                    user=self.context['request'].user
                )
                quantity = Decimal(str(item_data['quantity']))
                unit_price = Decimal(str(item_data.get('unit_price', product.selling_price)))
                
                # Check stock availability
                if product.track_inventory and not product.can_sell(quantity):
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.name}. Available: {product.current_stock}"
                    )
                
                line_total = unit_price * quantity
                subtotal += line_total
                total_cost += product.cost_price * quantity
                
            except Product.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {item_data['product_id']} not found")
        
        validated_data['subtotal'] = subtotal
        validated_data['total_amount'] = subtotal  # Simplified for prototype
        validated_data['amount_paid'] = validated_data.get('amount_paid', subtotal)
        
        # Create transaction
        transaction = super().create(validated_data)
        
        # Create transaction items and update stock
        for item_data in items_data:
            product = Product.objects.get(
                id=item_data['product_id'], 
                user=self.context['request'].user
            )
            quantity = Decimal(str(item_data['quantity']))
            unit_price = Decimal(str(item_data.get('unit_price', product.selling_price)))
            
            # Create transaction item
            TransactionItem.objects.create(
                transaction=transaction,
                product=product,
                product_name=product.name,
                quantity=quantity,
                unit_price=unit_price,
                unit_cost=product.cost_price,
                line_total=unit_price * quantity,
                discount_amount=Decimal(str(item_data.get('discount_amount', '0.00')))
            )
            
            # Update product stock and sales data
            if product.track_inventory:
                product.current_stock -= quantity
            product.total_sold += quantity
            product.total_revenue += unit_price * quantity
            product.last_sold_date = transaction.transaction_date
            product.save()
            
            # Create stock movement record
            from apps.inventory.models import StockMovement
            StockMovement.objects.create(
                product=product,
                movement_type='sale',
                quantity=quantity,
                unit_cost=product.cost_price,
                stock_before=product.current_stock + quantity,
                stock_after=product.current_stock,
                reference_number=transaction.transaction_number,
                created_by=self.context['request'].user
            )
        
        # Apply auto-save if enabled
        self._apply_auto_save(transaction)
        
        return transaction
    
    def _apply_auto_save(self, transaction):
        """Apply automatic savings from transaction"""
        user = transaction.user
        try:
            from apps.savings.models import SavingsAccount
            savings_account = SavingsAccount.objects.filter(
                user=user, 
                is_default=True, 
                auto_save_enabled=True,
                status='active'
            ).first()
            
            if savings_account and transaction.total_amount >= savings_account.auto_save_minimum:
                auto_save_amount = min(
                    (transaction.total_amount * savings_account.auto_save_percentage) / 100,
                    savings_account.auto_save_maximum
                )
                
                if auto_save_amount > 0:
                    savings_account.add_funds(
                        auto_save_amount,
                        transaction_type='auto_save',
                        reference=transaction.transaction_number
                    )
                    
                    transaction.auto_save_amount = auto_save_amount
                    transaction.auto_save_applied = True
                    transaction.save()
        except Exception:
            pass  # Don't fail transaction if auto-save fails


