from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from .models import Notification
from users.models import Follow
from posts.models import Post, Comment, Like

User = get_user_model()


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """Create notification when user follows another user."""
    if created:
        # Don't create notification for self-follows
        if instance.follower != instance.following:
            Notification.create_notification(
                recipient=instance.following,
                sender=instance.follower,
                notification_type='follow',
                title='New Follower',
                message=f'{instance.follower.username} started following you',
                data={
                    'follower_id': instance.follower.id,
                    'follower_username': instance.follower.username
                }
            )


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """Create notification when user likes a post."""
    if created:
        # Don't create notification for own likes
        if instance.user != instance.post.author:
            Notification.create_notification(
                recipient=instance.post.author,
                sender=instance.user,
                notification_type='like',
                title='New Like',
                message=f'{instance.user.username} liked your post',
                content_object=instance.post,
                data={
                    'post_id': instance.post.id,
                    'post_content': instance.post.content[:50] + '...' if len(instance.post.content) > 50 else instance.post.content
                }
            )


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """Create notification when user comments on a post."""
    if created:
        # Don't create notification for own comments
        if instance.author != instance.post.author:
            Notification.create_notification(
                recipient=instance.post.author,
                sender=instance.author,
                notification_type='comment',
                title='New Comment',
                message=f'{instance.author.username} commented on your post',
                content_object=instance.post,
                data={
                    'post_id': instance.post.id,
                    'comment_id': instance.id,
                    'comment_content': instance.content[:50] + '...' if len(instance.content) > 50 else instance.content,
                    'post_content': instance.post.content[:50] + '...' if len(instance.post.content) > 50 else instance.post.content
                }
            )


@receiver(post_save, sender=Comment)
def create_mention_notifications(sender, instance, created, **kwargs):
    """Create notifications for user mentions in comments."""
    if created:
        # Check for @mentions in comment content
        import re
        mentions = re.findall(r'@(\w+)', instance.content)
        
        for username in mentions:
            try:
                mentioned_user = User.objects.get(username=username, is_active=True)
                
                # Don't create notification for self-mentions
                if mentioned_user != instance.author:
                    # Check if user is mentioned in a comment on their own post
                    if mentioned_user != instance.post.author:
                        Notification.create_notification(
                            recipient=mentioned_user,
                            sender=instance.author,
                            notification_type='mention',
                            title='Mentioned in Comment',
                            message=f'{instance.author.username} mentioned you in a comment',
                            content_object=instance.post,
                            data={
                                'post_id': instance.post.id,
                                'comment_id': instance.id,
                                'comment_content': instance.content[:50] + '...' if len(instance.content) > 50 else instance.content
                            }
                        )
            except User.DoesNotExist:
                # User doesn't exist, skip
                pass


@receiver(post_delete, sender=Like)
def handle_like_deletion(sender, instance, **kwargs):
    """Handle like deletion (unlike)."""
    # No need to create notification for unlikes, just log for debugging
    print(f"Like removed: User {instance.user.username} unliked post {instance.post.id}")


@receiver(post_delete, sender=Follow)
def handle_follow_deletion(sender, instance, **kwargs):
    """Handle follow deletion (unfollow)."""
    # No need to create notification for unfollows, just log for debugging
    print(f"Follow removed: User {instance.follower.username} unfollowed {instance.following.username}")


# Signal to create notification preferences for new users
@receiver(post_save, sender=User)
def create_notification_preferences(sender, instance, created, **kwargs):
    """Create notification preferences for new users."""
    if created:
        from .models import NotificationPreference
        NotificationPreference.objects.get_or_create(user=instance)


