
# backend/apps/notifications/admin.py
"""
Notification admin
"""

from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__email']
    readonly_fields = ['created_at', 'read_at']


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'email_enabled', 'sms_enabled', 'push_enabled', 'is_active']
    list_filter = ['notification_type', 'is_active']
    search_fields = ['user__email']