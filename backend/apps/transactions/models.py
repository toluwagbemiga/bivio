# backend/apps/transactions/models.py
"""
Transaction models for POS sales and payments
"""

import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.inventory.models import Product


class Transaction(models.Model):
    """
    Main transaction model for POS sales
    """
    
    TRANSACTION_TYPES = [
        ('sale', 'Sale'),
        ('return', 'Return'),
        ('exchange', 'Exchange'),
        ('service', 'Service Payment'),
        ('loan_disbursement', 'Loan Disbursement'),
        ('loan_repayment', 'Loan Repayment'),
        ('savings_deposit', 'Savings Deposit'),
        ('savings_withdrawal', 'Savings Withdrawal'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('pos', 'POS Card'),
        ('transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('credit', 'Credit'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    # Transaction Details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, default='sale')
    transaction_number = models.CharField(max_length=50, unique=True)
    reference_number = models.CharField(max_length=100, blank=True)
    
    # Financial Details
    subtotal = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    tax_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Payment Information
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount_paid = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    change_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Customer Information
    customer_name = models.CharField(max_length=200, blank=True)
    customer_phone = models.CharField(max_length=15, blank=True)
    customer_email = models.EmailField(blank=True)
    
    # Status and Metadata
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='completed')
    notes = models.TextField(blank=True)
    
    # AI Categorization
    ai_category = models.CharField(max_length=100, blank=True)
    ai_confidence = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='AI categorization confidence score (0-1)'
    )
    
    # POS Device Information
    pos_device_serial = models.CharField(max_length=100, blank=True)
    pos_transaction_id = models.CharField(max_length=100, blank=True)
    
    # Location (optional)
    latitude = models.DecimalField(
        max_digits=10,
        decimal_places=8,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=11,
        decimal_places=8,
        null=True,
        blank=True
    )
    
    # Auto-save settings
    auto_save_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Amount automatically saved from this transaction'
    )
    auto_save_applied = models.BooleanField(default=False)
    
    # Timestamps
    transaction_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['user', 'transaction_date']),
            models.Index(fields=['transaction_number']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_method']),
        ]
    
    def __str__(self):
        return f"Transaction {self.transaction_number} - ₦{self.total_amount}"
    
    def save(self, *args, **kwargs):
        """Auto-generate transaction number if not provided"""
        if not self.transaction_number:
            from datetime import datetime
            date_str = datetime.now().strftime('%Y%m%d')
            user_id = str(self.user.id)[:8].upper()
            # Get transaction count for today
            today_count = Transaction.objects.filter(
                user=self.user,
                transaction_date__date=datetime.now().date()
            ).count() + 1
            self.transaction_number = f"TXN-{date_str}-{user_id}-{today_count:03d}"
        super().save(*args, **kwargs)
    
    @property
    def profit(self):
        """Calculate total profit for this transaction"""
        return sum(item.profit for item in self.transaction_items.all())
    
    @property
    def is_paid(self):
        """Check if transaction is fully paid"""
        return self.amount_paid >= self.total_amount


class TransactionItem(models.Model):
    """
    Individual items within a transaction
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        Transaction,
        on_delete=models.CASCADE,
        related_name='transaction_items'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='transaction_items'
    )
    
    # Item Details
    product_name = models.CharField(
        max_length=200,
        help_text='Product name at time of transaction'
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    unit_price = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Unit price at time of transaction'
    )
    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Unit cost at time of transaction'
    )
    
    # Calculated Fields
    line_total = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    discount_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    class Meta:
        db_table = 'transaction_items'
        verbose_name = _('Transaction Item')
        verbose_name_plural = _('Transaction Items')
        indexes = [
            models.Index(fields=['transaction']),
            models.Index(fields=['product']),
        ]
    
    def __str__(self):
        return f"{self.product_name} x {self.quantity} - ₦{self.line_total}"
    
    def save(self, *args, **kwargs):
        """Auto-calculate line total"""
        self.line_total = (self.unit_price * self.quantity) - self.discount_amount
        super().save(*args, **kwargs)
    
    @property
    def profit(self):
        """Calculate profit for this item"""
        return (self.unit_price - self.unit_cost) * self.quantity - self.discount_amount