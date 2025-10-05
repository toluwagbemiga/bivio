# backend/apps/analytics/serializers.py
"""
Analytics serializers for business insights and metrics
"""

from rest_framework import serializers
from .models import BusinessMetrics, CashFlowData, BusinessInsight, AlertRule


class BusinessMetricsSerializer(serializers.ModelSerializer):
    """
    Serializer for business metrics and performance data
    """
    
    class Meta:
        model = BusinessMetrics
        fields = [
            'id', 'period_type', 'period_start', 'period_end',
            'total_sales_amount', 'total_sales_count', 'average_transaction_value',
            'total_cost_of_goods', 'gross_profit', 'gross_profit_margin',
            'inventory_value', 'inventory_turnover', 'unique_customers',
            'repeat_customers', 'customer_retention_rate', 'cash_flow',
            'savings_amount', 'loan_repayments', 'top_selling_products',
            'slow_moving_products', 'days_active', 'peak_sales_hour',
            'ai_insights', 'performance_score', 'growth_rate', 'created_at'
        ]
        read_only_fields = [
            'id', 'total_sales_amount', 'total_sales_count', 
            'average_transaction_value', 'total_cost_of_goods', 'gross_profit',
            'gross_profit_margin', 'inventory_value', 'inventory_turnover',
            'unique_customers', 'repeat_customers', 'customer_retention_rate',
            'cash_flow', 'savings_amount', 'loan_repayments', 
            'top_selling_products', 'slow_moving_products', 'days_active',
            'peak_sales_hour', 'ai_insights', 'performance_score', 
            'growth_rate', 'created_at'
        ]


class CashFlowDataSerializer(serializers.ModelSerializer):
    """
    Serializer for cash flow data
    """
    
    class Meta:
        model = CashFlowData
        fields = [
            'id', 'flow_type', 'category', 'inflow_amount', 'outflow_amount',
            'net_flow', 'flow_date', 'description', 'reference_id',
            'is_predicted', 'confidence_score', 'created_at'
        ]
        read_only_fields = ['id', 'net_flow', 'created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class BusinessInsightSerializer(serializers.ModelSerializer):
    """
    Serializer for AI-generated business insights
    """
    is_expired = serializers.ReadOnlyField()
    is_high_confidence = serializers.ReadOnlyField()
    
    class Meta:
        model = BusinessInsight
        fields = [
            'id', 'insight_type', 'title', 'description', 'recommendations',
            'priority', 'potential_impact', 'estimated_benefit', 'model_version',
            'confidence_score', 'data_period_start', 'data_period_end',
            'data_sources', 'is_viewed', 'is_implemented', 'user_feedback',
            'user_rating', 'expires_at', 'is_expired', 'is_high_confidence',
            'created_at'
        ]
        read_only_fields = [
            'id', 'insight_type', 'title', 'description', 'recommendations',
            'priority', 'potential_impact', 'estimated_benefit', 'model_version',
            'confidence_score', 'data_period_start', 'data_period_end',
            'data_sources', 'expires_at', 'is_expired', 'is_high_confidence',
            'created_at'
        ]


class AlertRuleSerializer(serializers.ModelSerializer):
    """
    Serializer for custom alert rules
    """
    can_trigger = serializers.ReadOnlyField()
    
    class Meta:
        model = AlertRule
        fields = [
            'id', 'name', 'alert_type', 'description', 'metric_field',
            'operator', 'threshold_value', 'send_email', 'send_sms',
            'send_push', 'cooldown_hours', 'last_triggered', 'trigger_count',
            'is_active', 'can_trigger', 'created_at'
        ]
        read_only_fields = [
            'id', 'last_triggered', 'trigger_count', 'can_trigger', 'created_at'
        ]
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


