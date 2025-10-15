# backend/apps/users/urls.py
"""
URL configuration for user management
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BusinessProfileViewSet, GuarantorViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'business-profiles', BusinessProfileViewSet, basename='businessprofile')
router.register(r'guarantors', GuarantorViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
