# backend/apps/savings/models.py
"""
Savings and wallet models for micro-savings functionality
"""

import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class SavingsAccount(models.Model):
    """
    Main savings account for users
    """
    
    ACCOUNT_TYPES = [
        ('general', 'General Savings'),
        ('loan_repayment', 'Loan Repayment Buffer'),
        ('emergency', 'Emergency Fund'),
        ('business_growth', 'Business Growth'),
        ('goal_based', 'Goal-Based Savings'),
    ]
    
    ACCOUNT_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('frozen', 'Frozen'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='savings_accounts'
    )
    
    # Account Details
    account_number = models.CharField(max_length=20, unique=True)
    account_name = models.CharField(max_length=200)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='general')
    
    # Balance Information
    current_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    minimum_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    target_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Savings target amount (optional)'
    )
    
    # Auto-save Settings
    auto_save_enabled = models.BooleanField(
        default=False,
        help_text='Automatically save percentage from transactions'
    )
    auto_save_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5,
        validators=[MinValueValidator(Decimal('0.01')), MinValueValidator(Decimal('50.00'))],
        help_text='Percentage of each transaction to auto-save'
    )
    auto_save_minimum = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10,
        help_text='Minimum amount for auto-save to trigger'
    )
    auto_save_maximum = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1000,
        help_text='Maximum amount for single auto-save'
    )
    
    # Interest Settings
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Annual interest rate percentage'
    )
    last_interest_calculation = models.DateTimeField(null=True, blank=True)
    total_interest_earned = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Status
    status = models.CharField(max_length=20, choices=ACCOUNT_STATUS, default='active')
    is_default = models.BooleanField(
        default=False,
        help_text='Default savings account for auto-save'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'savings_accounts'
        verbose_name = _('Savings Account')
        verbose_name_plural = _('Savings Accounts')
        ordering = ['-is_default', 'account_name']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['account_number']),
            models.Index(fields=['account_type']),
        ]
    
    def __str__(self):
        return f"{self.account_name} - ₦{self.current_balance}"
    
    def save(self, *args, **kwargs):
        """Auto-generate account number"""
        if not self.account_number:
            user_id = str(self.user.id)[:8].upper()
            account_count = SavingsAccount.objects.filter(user=self.user).count() + 1
            self.account_number = f"SAV-{user_id}-{account_count:03d}"
        super().save(*args, **kwargs)
    
    @property
    def progress_percentage(self):
        """Calculate progress towards target"""
        if self.target_amount and self.target_amount > 0:
            return min((self.current_balance / self.target_amount) * 100, 100)
        return 0
    
    @property
    def remaining_to_target(self):
        """Amount remaining to reach target"""
        if self.target_amount:
            return max(self.target_amount - self.current_balance, 0)
        return 0
    
    def can_withdraw(self, amount):
        """Check if withdrawal amount is allowed"""
        return (self.current_balance - amount) >= self.minimum_balance
    
    def add_funds(self, amount, transaction_type='deposit', reference=''):
        """Add funds to savings account"""
        if amount > 0:
            self.current_balance += amount
            self.save()
            
            # Create savings transaction record
            SavingsTransaction.objects.create(
                savings_account=self,
                transaction_type=transaction_type,
                amount=amount,
                reference=reference,
                balance_after=self.current_balance
            )
    
    def withdraw_funds(self, amount, transaction_type='withdrawal', reference=''):
        """Withdraw funds from savings account"""
        if amount > 0 and self.can_withdraw(amount):
            self.current_balance -= amount
            self.save()
            
            # Create savings transaction record
            SavingsTransaction.objects.create(
                savings_account=self,
                transaction_type=transaction_type,
                amount=-amount,  # Negative for withdrawal
                reference=reference,
                balance_after=self.current_balance
            )
            return True
        return False


class SavingsTransaction(models.Model):
    """
    Individual savings transactions (deposits, withdrawals, auto-saves)
    """
    
    TRANSACTION_TYPES = [
        ('deposit', 'Manual Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('auto_save', 'Auto-save from Transaction'),
        ('interest', 'Interest Payment'),
        ('penalty', 'Penalty Deduction'),
        ('transfer_in', 'Transfer In'),
        ('transfer_out', 'Transfer Out'),
        ('loan_deduction', 'Loan Collateral Deduction'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    savings_account = models.ForeignKey(
        SavingsAccount,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    
    # Transaction Details
    transaction_reference = models.CharField(max_length=100, unique=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Positive for deposits, negative for withdrawals'
    )
    
    # Source/Reference Information
    reference = models.CharField(
        max_length=200,
        blank=True,
        help_text='Reference to source transaction or reason'
    )
    source_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='ID of source POS transaction for auto-save'
    )
    
    # Balance Information
    balance_before = models.DecimalField(max_digits=15, decimal_places=2)
    balance_after = models.DecimalField(max_digits=15, decimal_places=2)
    
    # Status and Notes
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='completed')
    notes = models.TextField(blank=True)
    
    # Processing Information
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_savings_transactions'
    )
    
    # Timestamps
    transaction_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'savings_transactions'
        verbose_name = _('Savings Transaction')
        verbose_name_plural = _('Savings Transactions')
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['savings_account', 'transaction_date']),
            models.Index(fields=['transaction_reference']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['source_transaction_id']),
        ]
    
    def __str__(self):
        return f"{self.transaction_type.title()} - ₦{abs(self.amount)}"
    
    def save(self, *args, **kwargs):
        """Auto-generate transaction reference and set balance_before"""
        if not self.transaction_reference:
            date_str = self.transaction_date.strftime('%Y%m%d') if self.transaction_date else datetime.now().strftime('%Y%m%d')
            account_id = str(self.savings_account.id)[:8].upper()
            transaction_count = SavingsTransaction.objects.filter(savings_account=self.savings_account).count() + 1
            self.transaction_reference = f"SVG-{date_str}-{account_id}-{transaction_count:03d}"
        
        if not self.balance_before:
            self.balance_before = self.savings_account.current_balance
        
        super().save(*args, **kwargs)
    
    @property
    def is_credit(self):
        """Check if transaction is a credit (positive amount)"""
        return self.amount > 0
    
    @property
    def is_debit(self):
        """Check if transaction is a debit (negative amount)"""
        return self.amount < 0


class SavingsGoal(models.Model):
    """
    Specific savings goals for users
    """
    
    GOAL_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    savings_account = models.ForeignKey(
        SavingsAccount,
        on_delete=models.CASCADE,
        related_name='goals'
    )
    
    # Goal Details
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('100.00'))]
    )
    current_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Timeline
    target_date = models.DateField()
    monthly_target = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Calculated monthly savings needed'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=GOAL_STATUS, default='active')
    completed_date = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'savings_goals'
        verbose_name = _('Savings Goal')
        verbose_name_plural = _('Savings Goals')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['savings_account', 'status']),
            models.Index(fields=['target_date']),
        ]
    
    def __str__(self):
        return f"{self.name} - ₦{self.target_amount}"
    
    @property
    def progress_percentage(self):
        """Calculate completion percentage"""
        if self.target_amount > 0:
            return min((self.current_amount / self.target_amount) * 100, 100)
        return 0
    
    @property
    def remaining_amount(self):
        """Amount remaining to reach goal"""
        return max(self.target_amount - self.current_amount, 0)
    
    @property
    def days_remaining(self):
        """Days remaining to target date"""
        from datetime import date
        if self.target_date >= date.today():
            return (self.target_date - date.today()).days
        return 0
    
    def calculate_monthly_target(self):
        """Calculate monthly savings needed"""
        months_remaining = max(self.days_remaining / 30, 1)
        self.monthly_target = self.remaining_amount / months_remaining
        self.save()
        return self.monthly_target