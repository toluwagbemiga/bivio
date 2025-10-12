# backend/apps/notifications/urls.py
"""
URL configuration for notifications
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NotificationViewSet, NotificationPreferenceViewSet

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet)
router.register(r'preferences', NotificationPreferenceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]