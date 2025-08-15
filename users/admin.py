from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Follow


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_deactivated', 'date_joined')
    list_filter = ('role', 'is_active', 'is_deactivated', 'is_staff', 'is_superuser', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile', {
            'fields': ('bio', 'avatar_url', 'website', 'location', 'profile_visibility')
        }),
        ('Role & Status', {
            'fields': ('role', 'is_deactivated', 'deactivated_at')
        }),
        ('Email Verification', {
            'fields': ('is_email_verified', 'email_verification_token', 'email_verification_expires')
        }),
        ('Password Reset', {
            'fields': ('password_reset_token', 'password_reset_expires')
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login', 'deactivated_at')
    
    def get_queryset(self, request):
        """Show all users including deactivated ones."""
        return super().get_queryset(request)
    
    def save_model(self, request, obj, form, change):
        """Handle deactivation timestamp."""
        if 'is_deactivated' in form.changed_data and obj.is_deactivated:
            from django.utils import timezone
            obj.deactivated_at = timezone.now()
        super().save_model(request, obj, form, change)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Admin for Follow model."""
    
    list_display = ('follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    ordering = ('-created_at',)
    
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        """Prevent manual creation of follow relationships."""
        return False


