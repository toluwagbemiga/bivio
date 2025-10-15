# backend/apps/analytics/views.py
"""
Analytics and reporting API views for business intelligence
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from django.db import transaction as db_transaction
from datetime import datetime, timedelta
from decimal import Decimal

from .models import BusinessMetrics, CashFlowData, BusinessInsight, AlertRule
from .serializers import (
    BusinessMetricsSerializer,
    CashFlowDataSerializer,
    BusinessInsightSerializer,
    AlertRuleSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for analytics views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class BusinessMetricsViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing business metrics and performance data
    """
    queryset = BusinessMetrics.objects.all()
    serializer_class = BusinessMetricsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter metrics by user"""
        return BusinessMetrics.objects.filter(user=self.request.user).order_by('-period_start')
    
    def perform_create(self, serializer):
        """Set user when creating metrics"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get dashboard metrics"""
        today = timezone.now().date()
        this_month = timezone.now().replace(day=1).date()
        
        # Get latest metrics
        daily_metrics = self.get_queryset().filter(
            period_type='daily',
            period_start=today
        ).first()
        
        monthly_metrics = self.get_queryset().filter(
            period_type='monthly',
            period_start=this_month
        ).first()
        
        dashboard_data = {
            'today': BusinessMetricsSerializer(daily_metrics).data if daily_metrics else {},
            'this_month': BusinessMetricsSerializer(monthly_metrics).data if monthly_metrics else {},
            'quick_stats': self._get_quick_stats(request.user)
        }
        
        return Response(dashboard_data)
    
    def _get_quick_stats(self, user):
        """Get quick statistics for dashboard"""
        try:
            from apps.transactions.models import Transaction
            from apps.inventory.models import Product
            from apps.savings.models import SavingsAccount
            
            # Sales stats
            today_transactions = Transaction.objects.filter(
                user=user,
                transaction_date__date=timezone.now().date(),
                transaction_type='sale'
            )
            
            # Inventory stats
            products = Product.objects.filter(user=user)
            
            # Savings stats
            savings_accounts = SavingsAccount.objects.filter(user=user)
            
            return {
                'today_sales': sum(t.total_amount for t in today_transactions),
                'today_transactions': today_transactions.count(),
                'total_products': products.count(),
                'low_stock_products': products.filter(is_low_stock=True).count(),
                'total_savings': sum(sa.current_balance for sa in savings_accounts),
                'active_savings_accounts': savings_accounts.filter(status='active').count()
            }
        except ImportError:
            return {}
    
    @action(detail=False, methods=['post'])
    def generate_metrics(self, request):
        """Generate metrics for a specific period"""
        period_type = request.data.get('period_type', 'daily')
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Start date and end date are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if metrics already exist
        existing_metrics = BusinessMetrics.objects.filter(
            user=request.user,
            period_type=period_type,
            period_start=start_date
        ).first()
        
        if existing_metrics:
            return Response(
                {'error': 'Metrics for this period already exist'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create new metrics
        metrics = BusinessMetrics.objects.create(
            user=request.user,
            period_type=period_type,
            period_start=start_date,
            period_end=end_date
        )
        
        # Calculate metrics
        metrics.calculate_metrics()
        
        serializer = self.get_serializer(metrics)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def performance_trends(self, request):
        """Get performance trends over time"""
        days = int(request.query_params.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        
        metrics = self.get_queryset().filter(
            period_type='daily',
            period_start__gte=since_date.date()
        ).order_by('period_start')
        
        trends = {
            'dates': [],
            'sales': [],
            'transactions': [],
            'profit_margin': [],
            'performance_score': []
        }
        
        for metric in metrics:
            trends['dates'].append(metric.period_start.strftime('%Y-%m-%d'))
            trends['sales'].append(float(metric.total_sales_amount))
            trends['transactions'].append(metric.total_sales_count)
            trends['profit_margin'].append(float(metric.gross_profit_margin))
            trends['performance_score'].append(metric.performance_score)
        
        return Response(trends)


class CashFlowDataViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cash flow data
    """
    queryset = CashFlowData.objects.all()
    serializer_class = CashFlowDataSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter cash flow data by user"""
        return CashFlowData.objects.filter(user=self.request.user).order_by('-flow_date')
    
    def perform_create(self, serializer):
        """Set user when creating cash flow data"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get cash flow summary"""
        days = int(request.query_params.get('days', 30))
        since_date = timezone.now() - timedelta(days=days)
        
        cash_flow_data = self.get_queryset().filter(flow_date__gte=since_date.date())
        
        summary = {
            'total_inflows': sum(cf.inflow_amount for cf in cash_flow_data),
            'total_outflows': sum(cf.outflow_amount for cf in cash_flow_data),
            'net_cash_flow': sum(cf.net_flow for cf in cash_flow_data),
            'by_category': {},
            'by_type': {},
            'daily_breakdown': []
        }
        
        # By category
        for category, _ in CashFlowData.FLOW_CATEGORIES:
            category_data = cash_flow_data.filter(category=category)
            summary['by_category'][category] = {
                'inflows': sum(cf.inflow_amount for cf in category_data),
                'outflows': sum(cf.outflow_amount for cf in category_data),
                'net': sum(cf.net_flow for cf in category_data)
            }
        
        # By type
        for flow_type, _ in CashFlowData.CASH_FLOW_TYPES:
            type_data = cash_flow_data.filter(flow_type=flow_type)
            summary['by_type'][flow_type] = {
                'inflows': sum(cf.inflow_amount for cf in type_data),
                'outflows': sum(cf.outflow_amount for cf in type_data),
                'net': sum(cf.net_flow for cf in type_data)
            }
        
        # Daily breakdown
        for i in range(days):
            date = (timezone.now() - timedelta(days=i)).date()
            day_data = cash_flow_data.filter(flow_date=date)
            
            daily_summary = {
                'date': date,
                'inflows': sum(cf.inflow_amount for cf in day_data),
                'outflows': sum(cf.outflow_amount for cf in day_data),
                'net': sum(cf.net_flow for cf in day_data)
            }
            summary['daily_breakdown'].append(daily_summary)
        
        return Response(summary)
    
    @action(detail=False, methods=['post'])
    def generate_from_transactions(self, request):
        """Generate cash flow data from transactions"""
        start_date = request.data.get('start_date')
        end_date = request.data.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Start date and end date are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            from apps.transactions.models import Transaction
            
            transactions = Transaction.objects.filter(
                user=request.user,
                transaction_date__date__gte=start_date,
                transaction_date__date__lte=end_date,
                status='completed'
            )
            
            generated_count = 0
            
            for transaction in transactions:
                # Determine flow type and category
                if transaction.transaction_type == 'sale':
                    flow_type = 'operating'
                    category = 'sales_revenue'
                    inflow_amount = transaction.total_amount
                    outflow_amount = 0
                elif transaction.transaction_type == 'purchase':
                    flow_type = 'operating'
                    category = 'inventory_purchase'
                    inflow_amount = 0
                    outflow_amount = transaction.total_amount
                else:
                    continue
                
                # Create cash flow data
                CashFlowData.objects.get_or_create(
                    user=request.user,
                    flow_type=flow_type,
                    category=category,
                    flow_date=transaction.transaction_date.date(),
                    reference_id=str(transaction.id),
                    defaults={
                        'inflow_amount': inflow_amount,
                        'outflow_amount': outflow_amount,
                        'description': f"{transaction.get_transaction_type_display()} - {transaction.transaction_number}"
                    }
                )
                generated_count += 1
            
            return Response({
                'message': f'Generated {generated_count} cash flow records',
                'generated_count': generated_count
            })
            
        except ImportError:
            return Response(
                {'error': 'Transaction model not available'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BusinessInsightViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing AI-generated business insights
    """
    queryset = BusinessInsight.objects.all()
    serializer_class = BusinessInsightSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter insights by user"""
        return BusinessInsight.objects.filter(user=self.request.user).order_by('-priority', '-created_at')
    
    def perform_create(self, serializer):
        """Set user when creating insight"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread insights"""
        insights = self.get_queryset().filter(is_viewed=False)
        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def high_priority(self, request):
        """Get high priority insights"""
        insights = self.get_queryset().filter(priority__in=['high', 'critical'])
        serializer = self.get_serializer(insights, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_viewed(self, request, pk=None):
        """Mark insight as viewed"""
        insight = self.get_object()
        insight.is_viewed = True
        insight.save()
        
        serializer = self.get_serializer(insight)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_implemented(self, request, pk=None):
        """Mark insight as implemented"""
        insight = self.get_object()
        insight.is_implemented = True
        insight.user_feedback = request.data.get('feedback', '')
        insight.save()
        
        serializer = self.get_serializer(insight)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        """Rate insight quality"""
        insight = self.get_object()
        rating = request.data.get('rating')
        
        if not rating or not (1 <= rating <= 5):
            return Response(
                {'error': 'Rating must be between 1 and 5'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        insight.user_rating = rating
        insight.user_feedback = request.data.get('feedback', '')
        insight.save()
        
        serializer = self.get_serializer(insight)
        return Response(serializer.data)


class AlertRuleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing custom alert rules
    """
    queryset = AlertRule.objects.all()
    serializer_class = AlertRuleSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter alert rules by user"""
        return AlertRule.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set user when creating alert rule"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active alert rules"""
        rules = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(rules, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test alert rule with current data"""
        rule = self.get_object()
        
        # This is a simplified test - in production, you'd evaluate against actual data
        test_value = Decimal(str(request.data.get('test_value', 0)))
        
        condition_met = rule.evaluate_condition(test_value)
        
        return Response({
            'rule_name': rule.name,
            'test_value': test_value,
            'threshold_value': rule.threshold_value,
            'operator': rule.operator,
            'condition_met': condition_met,
            'can_trigger': rule.can_trigger()
        })
    
    @action(detail=True, methods=['post'])
    def trigger(self, request, pk=None):
        """Manually trigger alert rule"""
        rule = self.get_object()
        
        if not rule.can_trigger():
            return Response(
                {'error': 'Alert rule cannot be triggered at this time'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update trigger information
        rule.last_triggered = timezone.now()
        rule.trigger_count += 1
        rule.save()
        
        # In production, you would send actual notifications here
        return Response({
            'message': 'Alert triggered successfully',
            'trigger_count': rule.trigger_count,
            'last_triggered': rule.last_triggered
        })