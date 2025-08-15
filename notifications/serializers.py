from rest_framework import serializers
from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    recipient_username = serializers.CharField(source='recipient.username', read_only=True)
    notification_text = serializers.CharField(source='get_notification_text', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'recipient_username', 'sender', 'sender_username',
            'notification_type', 'title', 'message', 'notification_text',
            'content_type', 'object_id', 'data', 'is_read', 'is_archived',
            'created_at', 'read_at'
        ]
        read_only_fields = ['id', 'created_at', 'read_at']


class NotificationListSerializer(serializers.ModelSerializer):
    """Serializer for notification lists."""
    
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    notification_text = serializers.CharField(source='get_notification_text', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id', 'sender_username', 'notification_type', 'title', 'message',
            'notification_text', 'is_read', 'is_archived', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class NotificationCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating notifications."""
    
    class Meta:
        model = Notification
        fields = ['recipient', 'sender', 'notification_type', 'title', 'message', 'data']


class NotificationUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating notifications."""
    
    class Meta:
        model = Notification
        fields = ['is_read', 'is_archived']


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for notification preferences."""
    
    class Meta:
        model = NotificationPreference
        fields = [
            'email_follows', 'email_likes', 'email_comments', 'email_mentions', 'email_system',
            'push_follows', 'push_likes', 'push_comments', 'push_mentions', 'push_system',
            'in_app_follows', 'in_app_likes', 'in_app_comments', 'in_app_mentions', 'in_app_system',
            'quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end'
        ]


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics."""
    
    total_notifications = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    read_count = serializers.IntegerField()
    archived_count = serializers.IntegerField()
    
    # Counts by type
    follow_count = serializers.IntegerField()
    like_count = serializers.IntegerField()
    comment_count = serializers.IntegerField()
    mention_count = serializers.IntegerField()
    system_count = serializers.IntegerField()


