# backend/apps/notifications/views.py
"""
Notification management API views for user alerts and reminders
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationPreferenceSerializer
)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for notification views"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user notifications
    """
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter notifications by user"""
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set user when creating notification"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = self.get_queryset().filter(is_read=False)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get urgent notifications"""
        notifications = self.get_queryset().filter(priority='urgent')
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """Get notifications by type"""
        notification_type = request.query_params.get('type')
        if not notification_type:
            return Response(
                {'error': 'Notification type is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notifications = self.get_queryset().filter(notification_type=notification_type)
        serializer = self.get_serializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        notification = self.get_object()
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        serializer = self.get_serializer(notification)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        updated_count = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'message': f'Marked {updated_count} notifications as read',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get notification dashboard statistics"""
        notifications = self.get_queryset()
        
        stats = {
            'total_notifications': notifications.count(),
            'unread_count': notifications.filter(is_read=False).count(),
            'urgent_count': notifications.filter(priority='urgent', is_read=False).count(),
            'by_type': {},
            'by_priority': {},
            'recent_notifications': []
        }
        
        # By type
        for notification_type, _ in Notification.NOTIFICATION_TYPES:
            count = notifications.filter(notification_type=notification_type).count()
            stats['by_type'][notification_type] = count
        
        # By priority
        for priority, _ in Notification.PRIORITY_LEVELS:
            count = notifications.filter(priority=priority).count()
            stats['by_priority'][priority] = count
        
        # Recent notifications (last 5)
        recent = notifications[:5]
        stats['recent_notifications'] = NotificationSerializer(recent, many=True).data
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def create_system_notification(self, request):
        """Create system notification (admin only)"""
        if request.user.user_type != 'admin':
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        title = request.data.get('title')
        message = request.data.get('message')
        notification_type = request.data.get('notification_type', 'system')
        priority = request.data.get('priority', 'medium')
        target_users = request.data.get('target_users', [])
        
        if not title or not message:
            return Response(
                {'error': 'Title and message are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_count = 0
        
        if target_users:
            # Send to specific users
            from apps.users.models import User
            users = User.objects.filter(id__in=target_users)
            for user in users:
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    metadata=request.data.get('metadata', {})
                )
                created_count += 1
        else:
            # Send to all users
            from apps.users.models import User
            users = User.objects.all()
            for user in users:
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    priority=priority,
                    metadata=request.data.get('metadata', {})
                )
                created_count += 1
        
        return Response({
            'message': f'Created {created_count} notifications',
            'created_count': created_count
        })
    
    @action(detail=False, methods=['post'])
    def cleanup_expired(self, request):
        """Clean up expired notifications (admin only)"""
        if request.user.user_type != 'admin':
            return Response(
                {'error': 'Permission denied'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        expired_notifications = Notification.objects.filter(
            expires_at__lt=timezone.now()
        )
        deleted_count = expired_notifications.count()
        expired_notifications.delete()
        
        return Response({
            'message': f'Deleted {deleted_count} expired notifications',
            'deleted_count': deleted_count
        })


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing notification preferences
    """
    queryset = NotificationPreference.objects.all()
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter preferences by user"""
        return NotificationPreference.objects.filter(user=self.request.user).order_by('notification_type')
    
    def perform_create(self, serializer):
        """Set user when creating preference"""
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active notification preferences"""
        preferences = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(preferences, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Bulk update notification preferences"""
        preferences_data = request.data.get('preferences', [])
        
        if not preferences_data:
            return Response(
                {'error': 'Preferences data is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_count = 0
        
        for pref_data in preferences_data:
            notification_type = pref_data.get('notification_type')
            if not notification_type:
                continue
            
            preference, created = NotificationPreference.objects.get_or_create(
                user=request.user,
                notification_type=notification_type,
                defaults={
                    'email_enabled': pref_data.get('email_enabled', True),
                    'sms_enabled': pref_data.get('sms_enabled', False),
                    'push_enabled': pref_data.get('push_enabled', True),
                    'in_app_enabled': pref_data.get('in_app_enabled', True),
                    'frequency': pref_data.get('frequency', 'immediately'),
                    'quiet_hours_start': pref_data.get('quiet_hours_start'),
                    'quiet_hours_end': pref_data.get('quiet_hours_end'),
                    'is_active': pref_data.get('is_active', True)
                }
            )
            
            if not created:
                # Update existing preference
                preference.email_enabled = pref_data.get('email_enabled', preference.email_enabled)
                preference.sms_enabled = pref_data.get('sms_enabled', preference.sms_enabled)
                preference.push_enabled = pref_data.get('push_enabled', preference.push_enabled)
                preference.in_app_enabled = pref_data.get('in_app_enabled', preference.in_app_enabled)
                preference.frequency = pref_data.get('frequency', preference.frequency)
                preference.quiet_hours_start = pref_data.get('quiet_hours_start', preference.quiet_hours_start)
                preference.quiet_hours_end = pref_data.get('quiet_hours_end', preference.quiet_hours_end)
                preference.is_active = pref_data.get('is_active', preference.is_active)
                preference.save()
            
            updated_count += 1
        
        return Response({
            'message': f'Updated {updated_count} notification preferences',
            'updated_count': updated_count
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get notification preferences summary"""
        preferences = self.get_queryset()
        
        summary = {
            'total_preferences': preferences.count(),
            'active_preferences': preferences.filter(is_active=True).count(),
            'email_enabled_count': preferences.filter(email_enabled=True).count(),
            'sms_enabled_count': preferences.filter(sms_enabled=True).count(),
            'push_enabled_count': preferences.filter(push_enabled=True).count(),
            'in_app_enabled_count': preferences.filter(in_app_enabled=True).count(),
            'by_frequency': {},
            'by_type': {}
        }
        
        # By frequency
        for frequency, _ in NotificationPreference.FREQUENCY_CHOICES:
            count = preferences.filter(frequency=frequency).count()
            summary['by_frequency'][frequency] = count
        
        # By type
        for notification_type, _ in Notification.NOTIFICATION_TYPES:
            count = preferences.filter(notification_type=notification_type).count()
            summary['by_type'][notification_type] = count
        
        return Response(summary)
    
    @action(detail=True, methods=['post'])
    def toggle_channel(self, request, pk=None):
        """Toggle specific notification channel"""
        preference = self.get_object()
        channel = request.data.get('channel')  # email, sms, push, in_app
        enabled = request.data.get('enabled', True)
        
        if channel not in ['email', 'sms', 'push', 'in_app']:
            return Response(
                {'error': 'Invalid channel. Must be email, sms, push, or in_app'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        setattr(preference, f'{channel}_enabled', enabled)
        preference.save()
        
        serializer = self.get_serializer(preference)
        return Response(serializer.data)