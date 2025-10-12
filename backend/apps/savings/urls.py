# backend/apps/savings/urls.py
"""
URL configuration for savings management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SavingsAccountViewSet, SavingsTransactionViewSet, SavingsGoalViewSet

router = DefaultRouter()
router.register(r'accounts', SavingsAccountViewSet)
router.register(r'transactions', SavingsTransactionViewSet)
router.register(r'goals', SavingsGoalViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
