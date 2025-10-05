# backend/apps/analytics/admin.py
"""
Analytics admin configuration
"""

from django.contrib import admin
from .models import BusinessMetrics, CashFlowData, BusinessInsight, AlertRule


@admin.register(BusinessMetrics)
class BusinessMetricsAdmin(admin.ModelAdmin):
    list_display = ['user', 'period_type', 'period_start', 'period_end', 'total_sales_amount', 'gross_profit', 'performance_score']
    list_filter = ['period_type', 'period_start']
    search_fields = ['user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(CashFlowData)
class CashFlowDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'flow_type', 'category', 'inflow_amount', 'outflow_amount', 'net_flow', 'flow_date']
    list_filter = ['flow_type', 'category', 'is_predicted', 'flow_date']
    search_fields = ['user__email', 'reference_id']
    readonly_fields = ['net_flow', 'created_at']


@admin.register(BusinessInsight)
class BusinessInsightAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'insight_type', 'priority', 'confidence_score', 'is_viewed', 'created_at']
    list_filter = ['insight_type', 'priority', 'is_viewed', 'is_implemented']
    search_fields = ['title', 'description', 'user__email']
    readonly_fields = ['model_version', 'confidence_score', 'is_expired', 'is_high_confidence', 'created_at']


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'alert_type', 'operator', 'threshold_value', 'is_active', 'trigger_count']
    list_filter = ['alert_type', 'is_active', 'operator']
    search_fields = ['name', 'user__email']
    readonly_fields = ['last_triggered', 'trigger_count', 'created_at']