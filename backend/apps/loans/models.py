# backend/apps/loans/models.py
"""
Loan management models for POS Financial Management App
Handles loan applications, disbursements, and repayments
"""

import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class LoanProduct(models.Model):
    """
    Different loan products offered by lenders
    """
    
    INTEREST_TYPES = [
        ('fixed', 'Fixed Rate'),
        ('reducing', 'Reducing Balance'),
        ('flat', 'Flat Rate'),
    ]
    
    REPAYMENT_FREQUENCIES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('bi_weekly', 'Bi-Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    
    # Loan Terms
    min_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1000.00'))],
        help_text='Minimum loan amount in Naira'
    )
    max_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1000.00'))],
        help_text='Maximum loan amount in Naira'
    )
    
    # Interest and Fees
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text='Interest rate percentage per annum'
    )
    interest_type = models.CharField(max_length=20, choices=INTEREST_TYPES, default='reducing')
    
    processing_fee_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('100.00'))],
        help_text='Processing fee as percentage of loan amount'
    )
    
    # Repayment Terms
    min_tenure_days = models.PositiveIntegerField(
        default=30,
        help_text='Minimum loan tenure in days'
    )
    max_tenure_days = models.PositiveIntegerField(
        default=365,
        help_text='Maximum loan tenure in days'
    )
    repayment_frequency = models.CharField(max_length=20, choices=REPAYMENT_FREQUENCIES, default='weekly')
    
    # Eligibility Criteria
    min_credit_score = models.PositiveIntegerField(default=300)
    min_monthly_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=50000,
        help_text='Minimum monthly business revenue required'
    )
    min_business_age_months = models.PositiveIntegerField(
        default=6,
        help_text='Minimum business age in months'
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_loan_products'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loan_products'
        verbose_name = _('Loan Product')
        verbose_name_plural = _('Loan Products')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} - {self.interest_rate}% p.a."


class Loan(models.Model):
    """
    Individual loan records
    """
    
    LOAN_STATUS = [
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('disbursed', 'Disbursed'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('defaulted', 'Defaulted'),
        ('written_off', 'Written Off'),
    ]
    
    COLLATERAL_TYPES = [
        ('none', 'No Collateral'),
        ('guarantor', 'Guarantor'),
        ('pos_device', 'POS Device'),
        ('inventory', 'Business Inventory'),
        ('savings', 'Savings Deposit'),
        ('group', 'Group Guarantee'),
        ('digital', 'Digital Reputation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='loans'
    )
    loan_product = models.ForeignKey(
        LoanProduct,
        on_delete=models.PROTECT,
        related_name='loans'
    )
    
    # Loan Identification
    loan_number = models.CharField(max_length=50, unique=True)
    application_date = models.DateTimeField(auto_now_add=True)
    
    # Loan Terms
    principal_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('1000.00'))]
    )
    interest_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text='Interest rate at time of loan approval'
    )
    tenure_days = models.PositiveIntegerField()
    processing_fee = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Calculated Amounts
    total_interest = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Principal + Interest + Fees'
    )
    monthly_installment = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Expected monthly repayment amount'
    )
    
    # Repayment Tracking
    amount_paid = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    outstanding_balance = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Dates
    approved_date = models.DateTimeField(null=True, blank=True)
    disbursed_date = models.DateTimeField(null=True, blank=True)
    first_repayment_date = models.DateField(null=True, blank=True)
    final_repayment_date = models.DateField(null=True, blank=True)
    
    # Status and Risk
    status = models.CharField(max_length=20, choices=LOAN_STATUS, default='applied')
    days_past_due = models.PositiveIntegerField(default=0)
    risk_level = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Low Risk'),
            ('medium', 'Medium Risk'),
            ('high', 'High Risk'),
            ('critical', 'Critical Risk'),
        ],
        default='low'
    )
    
    # Collateral Information
    collateral_type = models.CharField(max_length=20, choices=COLLATERAL_TYPES, default='none')
    collateral_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True
    )
    collateral_description = models.TextField(blank=True)
    
    # Application Information
    purpose = models.TextField(help_text='Purpose of the loan')
    business_plan = models.TextField(blank=True, help_text='How loan will be used in business')
    
    # Decision Information
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_loans'
    )
    approval_notes = models.TextField(blank=True)
    rejection_reason = models.TextField(blank=True)
    
    # Auto-deduction Settings
    enable_auto_deduction = models.BooleanField(
        default=False,
        help_text='Automatically deduct percentage from POS transactions'
    )
    auto_deduction_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5,
        validators=[MinValueValidator(Decimal('1.00')), MaxValueValidator(Decimal('50.00'))],
        help_text='Percentage of each transaction to deduct for repayment'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loans'
        verbose_name = _('Loan')
        verbose_name_plural = _('Loans')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['borrower', 'status']),
            models.Index(fields=['loan_number']),
            models.Index(fields=['status']),
            models.Index(fields=['days_past_due']),
            models.Index(fields=['disbursed_date']),
        ]
    
    def __str__(self):
        return f"Loan {self.loan_number} - {self.borrower.get_full_name()}"
    
    def save(self, *args, **kwargs):
        """Auto-generate loan number and calculate amounts"""
        if not self.loan_number:
            date_str = datetime.now().strftime('%Y%m')
            user_id = str(self.borrower.id)[:8].upper()
            loan_count = Loan.objects.filter(borrower=self.borrower).count() + 1
            self.loan_number = f"LOAN-{date_str}-{user_id}-{loan_count:03d}"
        
        # Calculate total amounts
        self.processing_fee = (self.principal_amount * self.loan_product.processing_fee_rate) / 100
        
        if self.loan_product.interest_type == 'flat':
            self.total_interest = (self.principal_amount * self.interest_rate * self.tenure_days) / (365 * 100)
        else:  # reducing balance
            monthly_rate = self.interest_rate / (12 * 100)
            months = self.tenure_days / 30
            if monthly_rate > 0:
                self.monthly_installment = (self.principal_amount * monthly_rate * ((1 + monthly_rate) ** months)) / (((1 + monthly_rate) ** months) - 1)
                self.total_interest = (self.monthly_installment * months) - self.principal_amount
            else:
                self.monthly_installment = self.principal_amount / months
                self.total_interest = 0
        
        self.total_amount = self.principal_amount + self.total_interest + self.processing_fee
        
        if not self.outstanding_balance:
            self.outstanding_balance = self.total_amount
        
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        """Check if loan has overdue payments"""
        return self.days_past_due > 0 and self.outstanding_balance > 0
    
    @property
    def completion_percentage(self):
        """Calculate loan completion percentage"""
        if self.total_amount > 0:
            return ((self.total_amount - self.outstanding_balance) / self.total_amount) * 100
        return 0
    
    @property
    def next_payment_date(self):
        """Calculate next expected payment date"""
        if not self.first_repayment_date:
            return None
        
        # Find the most recent payment
        latest_payment = self.repayments.filter(status='completed').order_by('-payment_date').first()
        
        if latest_payment:
            base_date = latest_payment.payment_date.date()
        else:
            base_date = self.first_repayment_date
        
        if self.loan_product.repayment_frequency == 'weekly':
            return base_date + timedelta(weeks=1)
        elif self.loan_product.repayment_frequency == 'monthly':
            return base_date + timedelta(days=30)
        elif self.loan_product.repayment_frequency == 'daily':
            return base_date + timedelta(days=1)
        else:
            return base_date + timedelta(days=7)  # default to weekly


class LoanRepayment(models.Model):
    """
    Individual loan repayment records
    """
    
    REPAYMENT_TYPES = [
        ('scheduled', 'Scheduled Payment'),
        ('early', 'Early Payment'),
        ('auto_deduction', 'Auto-deduction'),
        ('manual', 'Manual Payment'),
        ('penalty', 'Penalty Payment'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loan = models.ForeignKey(
        Loan,
        on_delete=models.CASCADE,
        related_name='repayments'
    )
    
    # Payment Details
    payment_reference = models.CharField(max_length=100, unique=True)
    repayment_type = models.CharField(max_length=20, choices=REPAYMENT_TYPES)
    
    # Amounts
    scheduled_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Originally scheduled payment amount'
    )
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text='Actual amount paid'
    )
    principal_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Portion going to principal'
    )
    interest_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Portion going to interest'
    )
    penalty_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Late payment penalty'
    )
    
    # Payment Information
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', 'Cash'),
            ('bank_transfer', 'Bank Transfer'),
            ('auto_deduction', 'Auto-deduction from Sales'),
            ('mobile_money', 'Mobile Money'),
            ('pos', 'POS Payment'),
        ],
        default='cash'
    )
    transaction_reference = models.CharField(max_length=100, blank=True)
    
    # Dates
    due_date = models.DateField()
    payment_date = models.DateTimeField()
    
    # Status
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='completed')
    days_late = models.PositiveIntegerField(default=0)
    
    # Notes
    notes = models.TextField(blank=True)
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='processed_repayments'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loan_repayments'
        verbose_name = _('Loan Repayment')
        verbose_name_plural = _('Loan Repayments')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['loan', 'payment_date']),
            models.Index(fields=['payment_reference']),
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Payment {self.payment_reference} - ₦{self.paid_amount}"
    
    def save(self, *args, **kwargs):
        """Auto-generate payment reference and calculate late days"""
        if not self.payment_reference:
            date_str = self.payment_date.strftime('%Y%m%d')
            loan_id = str(self.loan.id)[:8].upper()
            payment_count = LoanRepayment.objects.filter(loan=self.loan).count() + 1
            self.payment_reference = f"PAY-{date_str}-{loan_id}-{payment_count:03d}"
        
        # Calculate days late
        if self.payment_date.date() > self.due_date:
            self.days_late = (self.payment_date.date() - self.due_date).days
        
        super().save(*args, **kwargs)


