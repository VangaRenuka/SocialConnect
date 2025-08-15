from django.contrib import admin
from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for Notification model."""
    
    list_display = ('id', 'recipient', 'sender', 'notification_type', 'title', 'is_read', 'is_archived', 'created_at')
    list_filter = ('notification_type', 'is_read', 'is_archived', 'created_at', 'recipient', 'sender')
    search_fields = ('title', 'message', 'recipient__username', 'sender__username')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('recipient', 'sender', 'notification_type', 'title', 'message')
        }),
        ('Content Reference', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Additional Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_read', 'is_archived')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'read_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'read_at')
    
    def get_queryset(self, request):
        """Show all notifications including archived ones."""
        return super().get_queryset(request).select_related('recipient', 'sender')
    
    def mark_as_read(self, request, queryset):
        """Mark selected notifications as read."""
        count = queryset.update(is_read=True)
        self.message_user(request, f'{count} notifications marked as read.')
    
    def mark_as_unread(self, request, queryset):
        """Mark selected notifications as unread."""
        count = queryset.update(is_read=False)
        self.message_user(request, f'{count} notifications marked as unread.')
    
    def archive_notifications(self, request, queryset):
        """Archive selected notifications."""
        count = queryset.update(is_archived=True)
        self.message_user(request, f'{count} notifications archived.')
    
    def unarchive_notifications(self, request, queryset):
        """Unarchive selected notifications."""
        count = queryset.update(is_archived=False)
        self.message_user(request, f'{count} notifications unarchived.')
    
    mark_as_read.short_description = "Mark selected notifications as read"
    mark_as_unread.short_description = "Mark selected notifications as unread"
    archive_notifications.short_description = "Archive selected notifications"
    unarchive_notifications.short_description = "Unarchive selected notifications"
    
    actions = [mark_as_read, mark_as_unread, archive_notifications, unarchive_notifications]


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin for NotificationPreference model."""
    
    list_display = ('user', 'email_follows', 'push_follows', 'in_app_follows', 'quiet_hours_enabled')
    list_filter = ('quiet_hours_enabled', 'email_follows', 'push_follows', 'in_app_follows')
    search_fields = ('user__username', 'user__email')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Email Preferences', {
            'fields': ('email_follows', 'email_likes', 'email_comments', 'email_mentions', 'email_system')
        }),
        ('Push Notification Preferences', {
            'fields': ('push_follows', 'push_likes', 'push_comments', 'push_mentions', 'push_system')
        }),
        ('In-App Notification Preferences', {
            'fields': ('in_app_follows', 'in_app_likes', 'in_app_comments', 'in_app_mentions', 'in_app_system')
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_enabled', 'quiet_hours_start', 'quiet_hours_end')
        }),
    )
    
    def get_queryset(self, request):
        """Show all notification preferences."""
        return super().get_queryset(request).select_related('user')


