# backend/apps/analytics/urls.py
"""
URL configuration for analytics and reporting
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessMetricsViewSet, CashFlowDataViewSet, BusinessInsightViewSet, AlertRuleViewSet

router = DefaultRouter()
router.register(r'metrics', BusinessMetricsViewSet)
router.register(r'cash-flow', CashFlowDataViewSet)
router.register(r'insights', BusinessInsightViewSet)
router.register(r'alerts', AlertRuleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
