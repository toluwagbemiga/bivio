# backend/apps/notifications/urls.py (UPDATE)
"""
Notification URLs
"""

from django.urls import path
from .views import (
    NotificationListView, NotificationDetailView, NotificationPreferenceView,
    mark_notification_read, mark_all_read, unread_count
)

urlpatterns = [
    path('', NotificationListView.as_view(), name='notification-list'),
    path('<uuid:pk>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('<uuid:pk>/mark-read/', mark_notification_read, name='mark-notification-read'),
    path('mark-all-read/', mark_all_read, name='mark-all-read'),
    path('unread-count/', unread_count, name='unread-count'),
    path('preferences/', NotificationPreferenceView.as_view(), name='notification-preferences'),
]

