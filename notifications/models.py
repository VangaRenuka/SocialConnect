from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Notification(models.Model):
    """Model for real-time notifications."""
    
    NOTIFICATION_TYPES = [
        ('follow', 'Follow'),
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('mention', 'Mention'),
        ('system', 'System'),
    ]
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        null=True,
        blank=True
    )
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=100)
    message = models.CharField(max_length=200)
    
    # Generic foreign key for related content (posts, comments, etc.)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Additional data for the notification
    data = models.JSONField(default=dict, blank=True)
    
    # Notification status
    is_read = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
    
    def __str__(self):
        return f"{self.notification_type} notification for {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            from django.utils import timezone
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def get_notification_text(self):
        """Get formatted notification text."""
        if self.notification_type == 'follow':
            return f"{self.sender.username} started following you"
        elif self.notification_type == 'like':
            return f"{self.sender.username} liked your post"
        elif self.notification_type == 'comment':
            return f"{self.sender.username} commented on your post"
        elif self.notification_type == 'mention':
            return f"{self.sender.username} mentioned you in a comment"
        elif self.notification_type == 'system':
            return self.message
        
        return self.message
    
    @classmethod
    def create_notification(cls, recipient, sender, notification_type, title, message, content_object=None, data=None):
        """Create a new notification."""
        notification = cls.objects.create(
            recipient=recipient,
            sender=sender,
            notification_type=notification_type,
            title=title,
            message=message,
            content_object=content_object,
            data=data or {}
        )
        
        # Send real-time notification via WebSocket
        from .consumers import send_notification_to_user
        send_notification_to_user(recipient.id, notification)
        
        return notification


class NotificationPreference(models.Model):
    """User preferences for notifications."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_preferences')
    
    # Email preferences
    email_follows = models.BooleanField(default=True)
    email_likes = models.BooleanField(default=True)
    email_comments = models.BooleanField(default=True)
    email_mentions = models.BooleanField(default=True)
    email_system = models.BooleanField(default=True)
    
    # Push notification preferences
    push_follows = models.BooleanField(default=True)
    push_likes = models.BooleanField(default=True)
    push_comments = models.BooleanField(default=True)
    push_mentions = models.BooleanField(default=True)
    push_system = models.BooleanField(default=True)
    
    # In-app notification preferences
    in_app_follows = models.BooleanField(default=True)
    in_app_likes = models.BooleanField(default=True)
    in_app_comments = models.BooleanField(default=True)
    in_app_mentions = models.BooleanField(default=True)
    in_app_system = models.BooleanField(default=True)
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(default=False)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Notification preferences for {self.user.username}"
    
    def should_send_notification(self, notification_type, method='in_app'):
        """Check if notification should be sent based on user preferences."""
        if method == 'email':
            return getattr(self, f'email_{notification_type}', True)
        elif method == 'push':
            return getattr(self, f'push_{notification_type}', True)
        elif method == 'in_app':
            return getattr(self, f'in_app_{notification_type}', True)
        
        return True
    
    def is_quiet_hours(self):
        """Check if current time is within quiet hours."""
        if not self.quiet_hours_enabled:
            return False
        
        from django.utils import timezone
        current_time = timezone.now().time()
        
        if self.quiet_hours_start and self.quiet_hours_end:
            if self.quiet_hours_start <= self.quiet_hours_end:
                return self.quiet_hours_start <= current_time <= self.quiet_hours_end
            else:  # Crosses midnight
                return current_time >= self.quiet_hours_start or current_time <= self.quiet_hours_end
        
        return False


