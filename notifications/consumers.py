import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

User = get_user_model()


class NotificationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time notifications."""
    
    async def connect(self):
        """Handle WebSocket connection."""
        self.user = self.scope["user"]
        
        if isinstance(self.user, AnonymousUser):
            await self.close()
            return
        
        # Create a unique group name for this user
        self.user_group_name = f"user_{self.user.id}"
        
        # Join the user's group
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to notifications',
            'user_id': self.user.id
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection."""
        # Leave the user's group
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages."""
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            if message_type == 'ping':
                # Respond to ping with pong
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': text_data_json.get('timestamp')
                }))
            
            elif message_type == 'get_notifications':
                # Send current unread notifications count
                unread_count = await self.get_unread_count()
                await self.send(text_data=json.dumps({
                    'type': 'notifications_count',
                    'unread_count': unread_count
                }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
    
    async def notification_message(self, event):
        """Send notification to WebSocket."""
        # Send notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'notification': event['notification']
        }))
    
    async def notification_update(self, event):
        """Send notification update to WebSocket."""
        # Send notification update to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'notification_update',
            'notification_id': event['notification_id'],
            'update_data': event['update_data']
        }))
    
    @database_sync_to_async
    def get_unread_count(self):
        """Get unread notifications count for the user."""
        from .models import Notification
        return Notification.objects.filter(
            recipient=self.user,
            is_read=False
        ).count()


# Function to send notifications to specific users
def send_notification_to_user(user_id, notification):
    """Send notification to a specific user via WebSocket."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    
    # Serialize notification data
    from .serializers import NotificationListSerializer
    notification_data = NotificationListSerializer(notification).data
    
    # Send to user's group
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            'type': 'notification_message',
            'notification': notification_data
        }
    )


def send_notification_update_to_user(user_id, notification_id, update_data):
    """Send notification update to a specific user via WebSocket."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    
    # Send update to user's group
    async_to_sync(channel_layer.group_send)(
        f"user_{user_id}",
        {
            'type': 'notification_update',
            'notification_id': notification_id,
            'update_data': update_data
        }
    )


# Broadcast notifications to all users (for system notifications)
def broadcast_notification(notification_data):
    """Broadcast notification to all connected users."""
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    
    channel_layer = get_channel_layer()
    
    # Send to a special broadcast group
    async_to_sync(channel_layer.group_send)(
        "broadcast",
        {
            'type': 'broadcast_notification',
            'notification': notification_data
        }
    )


