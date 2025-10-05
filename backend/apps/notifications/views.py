# backend/apps/notifications/views.py
"""
Notification views
"""

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from .models import Notification, NotificationPreference
from .serializers import NotificationSerializer, NotificationPreferenceSerializer


class NotificationListView(generics.ListAPIView):
    """
    List user's notifications
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['notification_type', 'is_read', 'priority']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """
    Get and update notification
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notification_read(request, pk):
    """
    Mark notification as read
    """
    try:
        notification = Notification.objects.get(id=pk, user=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        
        return Response({
            'message': 'Notification marked as read',
            'notification': NotificationSerializer(notification).data
        })
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_all_read(request):
    """
    Mark all notifications as read
    """
    updated = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True, read_at=timezone.now())
    
    return Response({
        'message': f'{updated} notifications marked as read',
        'count': updated
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def unread_count(request):
    """
    Get unread notification count
    """
    count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()
    
    return Response({'unread_count': count})


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """
    Get and update notification preferences
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        # Get or create default preferences
        notification_type = self.request.query_params.get('type', 'transaction')
        preference, created = NotificationPreference.objects.get_or_create(
            user=self.request.user,
            notification_type=notification_type
        )
        return preference


