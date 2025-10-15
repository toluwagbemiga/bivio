# apps/transactions/models.py - COMPLETE UNIFIED VERSION
"""
Complete Transaction System with:
- POS Sales & Purchases
- ERP Inventory Management
- Automatic Journal Entries
- Financial Statement Generation
"""

import uuid
from decimal import Decimal
from datetime import datetime
from django.db import models, transaction as db_transaction
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from apps.users.models import User
from apps.inventory.models import Product, ProductCategory


class TransactionCategory(models.Model):
    """
    Transaction categories - user selects BEFORE creating transaction
    """
    
    CATEGORY_TYPES = [
        ('sales', 'Sales'),
        ('purchase', 'Purchase'),
        ('expense', 'Expense'),
        ('inventory_in', 'Inventory Inward'),
        ('inventory_out', 'Inventory Outward'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category_type = models.CharField(max_length=20, choices=CATEGORY_TYPES)
    description = models.TextField(blank=True)
    
    # For remark parsing
    remark_keywords = models.TextField(
        blank=True,
        help_text='Keywords for auto-detection: indomie,milo,purchase'
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transaction_categories'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_type_display()})"


class Transaction(models.Model):
    """
    UNIFIED Transaction Model - Handles Everything:
    - POS Sales
    - Purchases
    - Inventory Movements
    - Auto Journal Entries
    - Financial Statement Data
    """
    
    TRANSACTION_TYPES = [
        ('sale', 'Sale'),
        ('purchase', 'Purchase'),
        ('return', 'Return'),
        ('adjustment', 'Adjustment'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('pos', 'POS Card'),
        ('bank_transfer', 'Bank Transfer'),
        ('mobile_money', 'Mobile Money'),
        ('credit', 'Credit'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    FLOW_DIRECTION = [
        ('inward', 'Inward (Stock/Money In)'),
        ('outward', 'Outward (Stock/Money Out)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    
    # CATEGORY FIRST - User must select before transaction
    transaction_category = models.ForeignKey(
        TransactionCategory,
        on_delete=models.PROTECT,
        related_name='transactions',
        help_text='Select category FIRST',
        default="cashflow",
    )
    
    # Transaction Details
    transaction_number = models.CharField(max_length=50, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    flow_direction = models.CharField(max_length=10, choices=FLOW_DIRECTION, default='inward', null=False, blank=False)
    
    # Amounts
    subtotal = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Payment
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    amount_paid = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Bank Transfer Remark (for auto-categorization)
    transaction_remark = models.TextField(
        blank=True,
        help_text='Bank remark: "Transfer for Indomie purchase"'
    )
    remark_parsed_data = models.JSONField(default=dict, blank=True)
    
    # Customer/Supplier
    counterparty_name = models.CharField(max_length=200, blank=True)
    counterparty_phone = models.CharField(max_length=15, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    notes = models.TextField(blank=True)
    
    # Accounting Integration
    journal_entry_created = models.BooleanField(default=False)
    journal_entry_reference = models.CharField(max_length=100, blank=True)
    
    # Auto-save
    auto_save_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    # Timestamps
    transaction_date = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['user', 'transaction_date']),
            models.Index(fields=['transaction_number']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.transaction_number} - ₦{self.total_amount}"
    
    def save(self, *args, **kwargs):
        # Auto-generate transaction number
        if not self.transaction_number:
            date_str = datetime.now().strftime('%Y%m%d')
            user_id = str(self.user.id)[:8].upper()
            count = Transaction.objects.filter(
                user=self.user,
                transaction_date__date=datetime.now().date()
            ).count() + 1
            self.transaction_number = f"TXN-{date_str}-{user_id}-{count:03d}"
        
        # Auto-determine flow direction
        if not self.flow_direction:
            self.flow_direction = 'inward' if self.transaction_type == 'sale' else 'outward'
        
        super().save(*args, **kwargs)
        
        # Create journal entry after saving
        if self.status == 'completed' and not self.journal_entry_created:
            self.create_journal_entry()
    
    def create_journal_entry(self):
        """
        AUTO-CREATE JOURNAL ENTRY
        This makes transaction appear in all financial statements
        """
        from apps.accounting.models import JournalEntry, JournalEntryLine, ChartOfAccounts
        
        try:
            with db_transaction.atomic():
                # Create journal entry
                entry = JournalEntry.objects.create(
                    user=self.user,
                    entry_date=self.transaction_date.date(),
                    description=f"{self.get_transaction_type_display()} - {self.transaction_number}",
                    reference_type='Transaction',
                    reference_id=str(self.id),
                    status='posted'
                )
                
                # Get or create accounts
                cash_account = ChartOfAccounts.objects.get_or_create(
                    user=self.user,
                    account_code='1010',
                    defaults={
                        'account_name': 'Cash',
                        'account_type': 'asset_current',
                        'account_category': 'cash',
                        'is_system_account': True
                    }
                )[0]
                
                if self.transaction_type == 'sale':
                    # Sale Transaction
                    sales_account = ChartOfAccounts.objects.get_or_create(
                        user=self.user,
                        account_code='4000',
                        defaults={
                            'account_name': 'Sales Revenue',
                            'account_type': 'revenue_sales',
                            'account_category': 'sales',
                            'is_system_account': True
                        }
                    )[0]
                    
                    cogs_account = ChartOfAccounts.objects.get_or_create(
                        user=self.user,
                        account_code='5000',
                        defaults={
                            'account_name': 'Cost of Goods Sold',
                            'account_type': 'expense_cogs',
                            'account_category': 'cogs',
                            'is_system_account': True
                        }
                    )[0]
                    
                    inventory_account = ChartOfAccounts.objects.get_or_create(
                        user=self.user,
                        account_code='1200',
                        defaults={
                            'account_name': 'Inventory',
                            'account_type': 'asset_current',
                            'account_category': 'inventory',
                            'is_system_account': True
                        }
                    )[0]
                    
                    # Dr. Cash, Cr. Sales
                    JournalEntryLine.objects.create(
                        journal_entry=entry,
                        account=cash_account,
                        debit_amount=self.total_amount,
                        credit_amount=0
                    )
                    
                    JournalEntryLine.objects.create(
                        journal_entry=entry,
                        account=sales_account,
                        debit_amount=0,
                        credit_amount=self.total_amount
                    )
                    
                    # Dr. COGS, Cr. Inventory (for cost)
                    total_cost = sum(item.unit_cost * item.quantity for item in self.items.all())
                    if total_cost > 0:
                        JournalEntryLine.objects.create(
                            journal_entry=entry,
                            account=cogs_account,
                            debit_amount=total_cost,
                            credit_amount=0
                        )
                        
                        JournalEntryLine.objects.create(
                            journal_entry=entry,
                            account=inventory_account,
                            debit_amount=0,
                            credit_amount=total_cost
                        )
                
                elif self.transaction_type == 'purchase':
                    # Purchase Transaction
                    inventory_account = ChartOfAccounts.objects.get_or_create(
                        user=self.user,
                        account_code='1200',
                        defaults={
                            'account_name': 'Inventory',
                            'account_type': 'asset_current',
                            'account_category': 'inventory',
                            'is_system_account': True
                        }
                    )[0]
                    
                    # Dr. Inventory, Cr. Cash
                    JournalEntryLine.objects.create(
                        journal_entry=entry,
                        account=inventory_account,
                        debit_amount=self.total_amount,
                        credit_amount=0
                    )
                    
                    JournalEntryLine.objects.create(
                        journal_entry=entry,
                        account=cash_account,
                        debit_amount=0,
                        credit_amount=self.total_amount
                    )
                
                # Mark as created
                self.journal_entry_created = True
                self.journal_entry_reference = entry.entry_number
                self.save(update_fields=['journal_entry_created', 'journal_entry_reference'])
                
        except Exception as e:
            print(f"Journal entry creation failed: {e}")


class TransactionItem(models.Model):
    """
    Items in a transaction
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    
    # Item details at time of transaction
    item_name = models.CharField(max_length=200,blank=False)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_price = models.DecimalField(max_digits=15, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=15, decimal_places=2)
    line_total = models.DecimalField(max_digits=15, decimal_places=2)
    
    class Meta:
        db_table = 'transaction_items'
    
    def __str__(self):
        return f"{self.item_name} x {self.quantity}"
    
    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)