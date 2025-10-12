# backend/apps/loans/urls.py
"""
URL configuration for loan management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoanProductViewSet, LoanViewSet, LoanRepaymentViewSet

router = DefaultRouter()
router.register(r'products', LoanProductViewSet)
router.register(r'loans', LoanViewSet)
router.register(r'repayments', LoanRepaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
