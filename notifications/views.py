from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth import get_user_model

from .models import Notification, NotificationPreference
from .serializers import (
    NotificationSerializer, NotificationListSerializer, NotificationUpdateSerializer,
    NotificationPreferenceSerializer, NotificationStatsSerializer
)

User = get_user_model()


class NotificationListView(generics.ListAPIView):
    """List user's notifications."""
    
    serializer_class = NotificationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for the current user."""
        user = self.request.user
        
        queryset = Notification.objects.filter(recipient=user).select_related('sender')
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            is_read = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read)
        
        # Filter by notification type
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by archived status
        is_archived = self.request.query_params.get('is_archived', None)
        if is_archived is not None:
            is_archived = is_archived.lower() == 'true'
            queryset = queryset.filter(is_archived=is_archived)
        
        return queryset


class NotificationDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve and update a notification."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get notifications for the current user."""
        return Notification.objects.filter(recipient=self.request.user).select_related('sender')
    
    def get_serializer_class(self):
        """Use different serializer for updates."""
        if self.request.method in ['PUT', 'PATCH']:
            return NotificationUpdateSerializer
        return NotificationSerializer


class NotificationMarkAsReadView(APIView):
    """Mark a notification as read."""
    
    def post(self, request, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )
        
        notification.mark_as_read()
        
        return Response({'message': 'Notification marked as read'}, status=status.HTTP_200_OK)


class NotificationMarkAllAsReadView(APIView):
    """Mark all user's notifications as read."""
    
    def post(self, request):
        # Mark all unread notifications as read
        unread_notifications = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        )
        
        count = unread_notifications.count()
        unread_notifications.update(is_read=True)
        
        return Response({
            'message': f'{count} notifications marked as read'
        }, status=status.HTTP_200_OK)


class NotificationArchiveView(APIView):
    """Archive a notification."""
    
    def post(self, request, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )
        
        notification.is_archived = True
        notification.save(update_fields=['is_archived'])
        
        return Response({'message': 'Notification archived'}, status=status.HTTP_200_OK)


class NotificationUnarchiveView(APIView):
    """Unarchive a notification."""
    
    def post(self, request, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )
        
        notification.is_archived = False
        notification.save(update_fields=['is_archived'])
        
        return Response({'message': 'Notification unarchived'}, status=status.HTTP_200_OK)


class NotificationDeleteView(APIView):
    """Delete a notification."""
    
    def delete(self, request, notification_id):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            recipient=request.user
        )
        
        notification.delete()
        
        return Response({'message': 'Notification deleted'}, status=status.HTTP_200_OK)


class NotificationStatsView(APIView):
    """Get notification statistics for the current user."""
    
    def get(self, request):
        user = request.user
        
        # Get notification counts
        notifications = Notification.objects.filter(recipient=user)
        
        stats = {
            'total_notifications': notifications.count(),
            'unread_count': notifications.filter(is_read=False).count(),
            'read_count': notifications.filter(is_read=True).count(),
            'archived_count': notifications.filter(is_archived=True).count(),
            
            # Counts by type
            'follow_count': notifications.filter(notification_type='follow').count(),
            'like_count': notifications.filter(notification_type='like').count(),
            'comment_count': notifications.filter(notification_type='comment').count(),
            'mention_count': notifications.filter(notification_type='mention').count(),
            'system_count': notifications.filter(notification_type='system').count(),
        }
        
        serializer = NotificationStatsSerializer(stats)
        return Response(serializer.data)


class NotificationPreferenceView(generics.RetrieveUpdateAPIView):
    """Get and update user's notification preferences."""
    
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create notification preferences for the current user."""
        preferences, created = NotificationPreference.objects.get_or_create(
            user=self.request.user
        )
        return preferences


class NotificationTestView(APIView):
    """Send a test notification to the current user."""
    
    def post(self, request):
        """Create a test notification."""
        user = request.user
        
        # Create a test notification
        notification = Notification.objects.create(
            recipient=user,
            sender=user,
            notification_type='system',
            title='Test Notification',
            message='This is a test notification to verify the system is working.'
        )
        
        return Response({
            'message': 'Test notification sent',
            'notification_id': notification.id
        }, status=status.HTTP_201_CREATED)


# Admin Views
class AdminNotificationListView(generics.ListAPIView):
    """Admin view for listing all notifications."""
    
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only admins can access this view."""
        if not self.request.user.is_admin():
            return Notification.objects.none()
        
        queryset = Notification.objects.all().select_related('recipient', 'sender')
        
        # Filter by recipient
        recipient = self.request.query_params.get('recipient', None)
        if recipient:
            queryset = queryset.filter(recipient__username=recipient)
        
        # Filter by notification type
        notification_type = self.request.query_params.get('type', None)
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by read status
        is_read = self.request.query_params.get('is_read', None)
        if is_read is not None:
            is_read = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read)
        
        return queryset


class AdminNotificationDeleteView(APIView):
    """Admin view for deleting any notification."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, notification_id):
        """Only admins can delete notifications."""
        if not request.user.is_admin():
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        notification = get_object_or_404(Notification, id=notification_id)
        notification.delete()
        
        return Response({'message': 'Notification deleted successfully'}, status=status.HTTP_200_OK)


