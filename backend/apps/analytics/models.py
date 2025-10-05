# backend/apps/analytics/models.py
"""
Analytics and business intelligence models
"""

import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class BusinessMetrics(models.Model):
    """
    Daily/Weekly/Monthly business metrics for users
    """
    
    PERIOD_TYPES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('quarterly', 'Quarterly'),
        ('yearly', 'Yearly'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='business_metrics'
    )
    
    # Period Information
    period_type = models.CharField(max_length=20, choices=PERIOD_TYPES)
    period_start = models.DateField()
    period_end = models.DateField()
    
    # Sales Metrics
    total_sales_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    total_sales_count = models.PositiveIntegerField(default=0)
    average_transaction_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Cost and Profit Metrics
    total_cost_of_goods = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    gross_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    gross_profit_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Gross profit margin percentage'
    )
    
    # Inventory Metrics
    inventory_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    inventory_turnover = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Inventory turnover ratio'
    )
    
    # Customer Metrics
    unique_customers = models.PositiveIntegerField(default=0)
    repeat_customers = models.PositiveIntegerField(default=0)
    customer_retention_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text='Customer retention percentage'
    )
    
    # Financial Health Metrics
    cash_flow = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Net cash flow for the period'
    )
    savings_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    loan_repayments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )
    
    # Product Performance
    top_selling_products = models.JSONField(
        default=list,
        help_text='List of top-selling products with quantities and revenue'
    )
    slow_moving_products = models.JSONField(
        default=list,
        help_text='Products with low sales velocity'
    )
    
    # Operational Metrics
    days_active = models.PositiveIntegerField(
        default=0,
        help_text='Number of days with transactions in period'
    )
    peak_sales_hour = models.TimeField(
        null=True,
        blank=True,
        help_text='Hour with highest sales activity'
    )
    
    # AI Insights
    ai_insights = models.JSONField(
        default=dict,
        help_text='AI-generated business insights and recommendations'
    )
    performance_score = models.PositiveIntegerField(
        default=0,
        help_text='Overall business performance score (0-100)'
    )
    
    # Comparison Metrics
    growth_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text='Growth rate compared to previous period (%)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'business_metrics'
        verbose_name = _('Business Metrics')
        verbose_name_plural = _('Business Metrics')
        ordering = ['-period_start']
        unique_together = ['user', 'period_type', 'period_start']
        indexes = [
            models.Index(fields=['user', 'period_type']),
            models.Index(fields=['period_start', 'period_end']),
            models.Index(fields=['total_sales_amount']),
            models.Index(fields=['performance_score']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.period_type.title()} - {self.period_start}"
    
    def calculate_metrics(self):
        """Calculate all metrics for the period"""
        from apps.transactions.models import Transaction
        from apps.inventory.models import Product
        from decimal import Decimal
        
        # Get transactions for the period
        transactions = Transaction.objects.filter(
            user=self.user,
            transaction_date__date__gte=self.period_start,
            transaction_date__date__lte=self.period_end,
            status='completed',
            transaction_type='sale'
        )
        
        # Sales Metrics
        self.total_sales_count = transactions.count()
        self.total_sales_amount = sum(t.total_amount for t in transactions) or Decimal('0.00')
        
        if self.total_sales_count > 0:
            self.average_transaction_value = self.total_sales_amount / self.total_sales_count
        
        # Cost and Profit Metrics
        total_cost = Decimal('0.00')
        for transaction in transactions:
            for item in transaction.transaction_items.all():
                total_cost += item.unit_cost * item.quantity
        
        self.total_cost_of_goods = total_cost
        self.gross_profit = self.total_sales_amount - total_cost
        
        if self.total_sales_amount > 0:
            self.gross_profit_margin = (self.gross_profit / self.total_sales_amount) * 100
        
        # Customer Metrics
        unique_phones = set()
        for t in transactions:
            if t.customer_phone:
                unique_phones.add(t.customer_phone)
        self.unique_customers = len(unique_phones)
        
        # Days Active
        active_dates = set(t.transaction_date.date() for t in transactions)
        self.days_active = len(active_dates)
        
        # Calculate performance score (0-100)
        self.performance_score = self._calculate_performance_score()
        
        self.save()
    
    def _calculate_performance_score(self):
        """Calculate overall business performance score"""
        score = 50  # Base score
        
        # Sales volume factor (0-25 points)
        if self.total_sales_amount >= 1000000:  # ₦1M+
            score += 25
        elif self.total_sales_amount >= 500000:  # ₦500K+
            score += 15
        elif self.total_sales_amount >= 200000:  # ₦200K+
            score += 10
        
        # Profit margin factor (0-20 points)
        if self.gross_profit_margin >= 30:
            score += 20
        elif self.gross_profit_margin >= 20:
            score += 15
        elif self.gross_profit_margin >= 10:
            score += 10
        
        # Activity factor (0-15 points)
        total_days = (self.period_end - self.period_start).days + 1
        activity_rate = (self.days_active / total_days) * 100
        if activity_rate >= 80:
            score += 15
        elif activity_rate >= 60:
            score += 10
        elif activity_rate >= 40:
            score += 5
        
        # Growth factor (0-10 points)
        if self.growth_rate >= 20:
            score += 10
        elif self.growth_rate >= 10:
            score += 7
        elif self.growth_rate >= 5:
            score += 5
        
        return min(score, 100)


class CashFlowData(models.Model):
    """
    Detailed cash flow tracking for businesses
    """
    
    CASH_FLOW_TYPES = [
        ('operating', 'Operating Activities'),
        ('investing', 'Investing Activities'),
        ('financing', 'Financing Activities'),
    ]
    
    FLOW_CATEGORIES = [
        ('sales_revenue', 'Sales Revenue'),
        ('inventory_purchase', 'Inventory Purchase'),
        ('loan_disbursement', 'Loan Disbursement'),
        ('loan_repayment', 'Loan Repayment'),
        ('savings_deposit', 'Savings Deposit'),
        ('savings_withdrawal', 'Savings Withdrawal'),
        ('expenses', 'Business Expenses'),
        ('taxes', 'Taxes and Fees'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cash_flow_data'
    )
    
    # Flow Details
    flow_type = models.CharField(max_length=20, choices=CASH_FLOW_TYPES)
    category = models.CharField(max_length=30, choices=FLOW_CATEGORIES)
    
    # Amounts
    inflow_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    outflow_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    net_flow = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0,
        help_text='Inflow - Outflow'
    )
    
    # Period
    flow_date = models.DateField()
    description = models.TextField(blank=True)
    
    # Reference
    reference_id = models.CharField(
        max_length=100,
        blank=True,
        help_text='Reference to source transaction/loan/etc.'
    )
    
    # Predicted vs Actual
    is_predicted = models.BooleanField(
        default=False,
        help_text='Whether this is a prediction or actual data'
    )
    confidence_score = models.FloatField(
        null=True,
        blank=True,
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='Confidence in prediction (if applicable)'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cash_flow_data'
        verbose_name = _('Cash Flow Data')
        verbose_name_plural = _('Cash Flow Data')
        ordering = ['-flow_date']
        indexes = [
            models.Index(fields=['user', 'flow_date']),
            models.Index(fields=['flow_type', 'category']),
            models.Index(fields=['is_predicted']),
        ]
    
    def __str__(self):
        return f"{self.category.replace('_', ' ').title()} - ₦{self.net_flow}"
    
    def save(self, *args, **kwargs):
        """Calculate net flow"""
        self.net_flow = self.inflow_amount - self.outflow_amount
        super().save(*args, **kwargs)


class BusinessInsight(models.Model):
    """
    AI-generated business insights and recommendations
    """
    
    INSIGHT_TYPES = [
        ('sales_trend', 'Sales Trend Analysis'),
        ('inventory_optimization', 'Inventory Optimization'),
        ('cash_flow_forecast', 'Cash Flow Forecast'),
        ('customer_behavior', 'Customer Behavior'),
        ('profitability', 'Profitability Analysis'),
        ('risk_assessment', 'Risk Assessment'),
        ('growth_opportunity', 'Growth Opportunity'),
        ('cost_optimization', 'Cost Optimization'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low Priority'),
        ('medium', 'Medium Priority'),
        ('high', 'High Priority'),
        ('critical', 'Critical'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='business_insights'
    )
    
    # Insight Details
    insight_type = models.CharField(max_length=30, choices=INSIGHT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Recommendations
    recommendations = models.JSONField(
        default=list,
        help_text='List of actionable recommendations'
    )
    
    # Priority and Impact
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    potential_impact = models.TextField(
        blank=True,
        help_text='Expected impact if recommendations are followed'
    )
    estimated_benefit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Estimated financial benefit in Naira'
    )
    
    # AI Model Information
    model_version = models.CharField(max_length=50, default='v1.0')
    confidence_score = models.FloatField(
        validators=[MinValueValidator(0.0), MaxValueValidator(1.0)],
        help_text='AI confidence in this insight'
    )
    
    # Data Sources
    data_period_start = models.DateField()
    data_period_end = models.DateField()
    data_sources = models.JSONField(
        default=list,
        help_text='List of data sources used for this insight'
    )
    
    # User Interaction
    is_viewed = models.BooleanField(default=False)
    is_implemented = models.BooleanField(default=False)
    user_feedback = models.TextField(blank=True)
    user_rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='User rating of insight quality (1-5 stars)'
    )
    
    # Expiry
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When this insight becomes irrelevant'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'business_insights'
        verbose_name = _('Business Insight')
        verbose_name_plural = _('Business Insights')
        ordering = ['-priority', '-created_at']
        indexes = [
            models.Index(fields=['user', 'insight_type']),
            models.Index(fields=['priority']),
            models.Index(fields=['is_viewed']),
            models.Index(fields=['confidence_score']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.priority.title()}"
    
    @property
    def is_expired(self):
        """Check if insight is expired"""
        from django.utils import timezone
        return self.expires_at and timezone.now() > self.expires_at
    
    @property
    def is_high_confidence(self):
        """Check if insight has high confidence"""
        return self.confidence_score >= 0.7


class AlertRule(models.Model):
    """
    Custom alert rules for business monitoring
    """
    
    ALERT_TYPES = [
        ('low_stock', 'Low Stock Alert'),
        ('high_sales', 'High Sales Alert'),
        ('low_sales', 'Low Sales Alert'),
        ('cash_flow_negative', 'Negative Cash Flow'),
        ('loan_payment_due', 'Loan Payment Due'),
        ('savings_goal_reached', 'Savings Goal Reached'),
        ('unusual_activity', 'Unusual Activity'),
        ('custom', 'Custom Rule'),
    ]
    
    COMPARISON_OPERATORS = [
        ('gt', 'Greater Than'),
        ('lt', 'Less Than'),
        ('eq', 'Equal To'),
        ('gte', 'Greater Than or Equal'),
        ('lte', 'Less Than or Equal'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='alert_rules'
    )
    
    # Rule Definition
    name = models.CharField(max_length=200)
    alert_type = models.CharField(max_length=30, choices=ALERT_TYPES)
    description = models.TextField(blank=True)
    
    # Condition
    metric_field = models.CharField(
        max_length=100,
        help_text='Field to monitor (e.g., current_stock, daily_sales)'
    )
    operator = models.CharField(max_length=10, choices=COMPARISON_OPERATORS)
    threshold_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text='Value to compare against'
    )
    
    # Notification Settings
    send_email = models.BooleanField(default=True)
    send_sms = models.BooleanField(default=False)
    send_push = models.BooleanField(default=True)
    
    # Frequency Control
    cooldown_hours = models.PositiveIntegerField(
        default=24,
        help_text='Hours to wait before sending another alert of same type'
    )
    last_triggered = models.DateTimeField(null=True, blank=True)
    trigger_count = models.PositiveIntegerField(default=0)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'alert_rules'
        verbose_name = _('Alert Rule')
        verbose_name_plural = _('Alert Rules')
        ordering = ['name']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['alert_type']),
            models.Index(fields=['last_triggered']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.user.get_full_name()}"
    
    def can_trigger(self):
        """Check if alert can be triggered based on cooldown"""
        if not self.is_active:
            return False
        
        if not self.last_triggered:
            return True
        
        from django.utils import timezone
        hours_since_last = (timezone.now() - self.last_triggered).total_seconds() / 3600
        return hours_since_last >= self.cooldown_hours
    
    def evaluate_condition(self, current_value):
        """Evaluate if the alert condition is met"""
        if self.operator == 'gt':
            return current_value > self.threshold_value
        elif self.operator == 'lt':
            return current_value < self.threshold_value
        elif self.operator == 'eq':
            return current_value == self.threshold_value
        elif self.operator == 'gte':
            return current_value >= self.threshold_value
        elif self.operator == 'lte':
            return current_value <= self.threshold_value
        return False