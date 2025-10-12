# backend/apps/transactions/urls.py
"""
URL configuration for transaction management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionCategoryViewSet, TransactionViewSet, TransactionItemViewSet

router = DefaultRouter()
router.register(r'categories', TransactionCategoryViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'items', TransactionItemViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
