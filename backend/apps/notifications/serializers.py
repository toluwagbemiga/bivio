# backend/apps/notifications/serializers.py
"""
Notification serializers
"""

from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for notifications
    """
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'notification_type', 'priority',
            'is_read', 'action_url', 'metadata', 'expires_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for notification preferences
    """
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'notification_type', 'email_enabled', 'sms_enabled',
            'push_enabled', 'in_app_enabled', 'frequency', 'quiet_hours_start',
            'quiet_hours_end', 'is_active'
        ]
        read_only_fields = ['id']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)