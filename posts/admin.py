from django.contrib import admin
from .models import Post, Comment, Like, PostImage


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin for Post model."""
    
    list_display = ('id', 'content', 'author', 'category', 'is_active', 'like_count', 'comment_count', 'created_at')
    list_filter = ('category', 'is_active', 'created_at', 'author')
    search_fields = ('content', 'author__username')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Content', {
            'fields': ('content', 'author', 'category', 'image_url')
        }),
        ('Status', {
            'fields': ('is_active', 'like_count', 'comment_count')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'like_count', 'comment_count')
    
    def get_queryset(self, request):
        """Show all posts including inactive ones."""
        return super().get_queryset(request).select_related('author')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for Comment model."""
    
    list_display = ('id', 'content', 'author', 'post', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at', 'author')
    search_fields = ('content', 'author__username', 'post__content')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Content', {
            'fields': ('content', 'author', 'post')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        """Show all comments including inactive ones."""
        return super().get_queryset(request).select_related('author', 'post')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin for Like model."""
    
    list_display = ('id', 'user', 'post', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__content')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Like Information', {
            'fields': ('user', 'post')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        """Show all likes."""
        return super().get_queryset(request).select_related('user', 'post')
    
    def has_add_permission(self, request):
        """Prevent manual creation of likes."""
        return False


@admin.register(PostImage)
class PostImageAdmin(admin.ModelAdmin):
    """Admin for PostImage model."""
    
    list_display = ('id', 'post', 'image', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('post__content',)
    ordering = ('-uploaded_at',)
    
    fieldsets = (
        ('Image Information', {
            'fields': ('post', 'image')
        }),
        ('Timestamps', {
            'fields': ('uploaded_at',)
        }),
    )
    
    readonly_fields = ('uploaded_at',)
    
    def get_queryset(self, request):
        """Show all post images."""
        return super().get_queryset(request).select_related('post')


