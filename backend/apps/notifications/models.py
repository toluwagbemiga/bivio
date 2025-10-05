# backend/apps/notifications/models.py
"""
Notification models for user alerts and reminders
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.users.models import User


class Notification(models.Model):
    """
    User notifications
    """
    
    NOTIFICATION_TYPES = [
        ('transaction', 'Transaction Alert'),
        ('loan_reminder', 'Loan Payment Reminder'),
        ('low_stock', 'Low Stock Alert'),
        ('savings_goal', 'Savings Goal Update'),
        ('system', 'System Notification'),
        ('promotion', 'Promotion'),
        ('warning', 'Warning'),
    ]
    
    PRIORITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    priority = models.CharField(max_length=20, choices=PRIORITY_LEVELS, default='medium')
    
    is_read = models.BooleanField(default=False)
    action_url = models.CharField(max_length=500, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.get_full_name()}"


class NotificationPreference(models.Model):
    """
    User notification preferences
    """
    
    FREQUENCY_CHOICES = [
        ('immediately', 'Immediately'),
        ('hourly', 'Hourly Digest'),
        ('daily', 'Daily Digest'),
        ('weekly', 'Weekly Digest'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences'
    )
    
    notification_type = models.CharField(max_length=20)
    email_enabled = models.BooleanField(default=True)
    sms_enabled = models.BooleanField(default=False)
    push_enabled = models.BooleanField(default=True)
    in_app_enabled = models.BooleanField(default=True)
    
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='immediately')
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        unique_together = ['user', 'notification_type']
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.notification_type}"


