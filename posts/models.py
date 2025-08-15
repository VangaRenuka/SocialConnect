from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator
from django.conf import settings
import os

User = get_user_model()


class Post(models.Model):
    """Model for user posts."""
    
    CATEGORY_CHOICES = [
        ('general', 'General'),
        ('announcement', 'Announcement'),
        ('question', 'Question'),
    ]
    
    content = models.TextField(max_length=280)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image_url = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    is_active = models.BooleanField(default=True)
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    
    class Meta:
        db_table = 'posts'
        ordering = ['-created_at']
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}..."
    
    def update_counts(self):
        """Update like and comment counts."""
        self.like_count = self.likes.count()
        self.comment_count = self.comments.filter(is_active=True).count()
        self.save(update_fields=['like_count', 'comment_count'])
    
    @property
    def is_liked_by_user(self, user):
        """Check if post is liked by a specific user."""
        if user.is_authenticated:
            return self.likes.filter(user=user).exists()
        return False


class Comment(models.Model):
    """Model for post comments."""
    
    content = models.TextField(max_length=200)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'comments'
        ordering = ['created_at']
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
    
    def __str__(self):
        return f"{self.author.username}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        """Update post comment count when comment is saved."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.post.update_counts()


class Like(models.Model):
    """Model for post likes."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'likes'
        unique_together = ('user', 'post')
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
    
    def __str__(self):
        return f"{self.user.username} likes {self.post.id}"
    
    def save(self, *args, **kwargs):
        """Update post like count when like is saved."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.post.update_counts()
    
    def delete(self, *args, **kwargs):
        """Update post like count when like is deleted."""
        super().delete(*args, **kwargs)
        self.post.update_counts()


class PostImage(models.Model):
    """Model for post images with validation."""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='post_images/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'post_images'
        verbose_name = 'Post Image'
        verbose_name_plural = 'Post Images'
    
    def __str__(self):
        return f"Image for post {self.post.id}"
    
    def clean(self):
        """Validate image size."""
        from django.core.exceptions import ValidationError
        
        if self.image:
            if self.image.size > settings.MAX_UPLOAD_SIZE:
                raise ValidationError(f'Image file too large. Size should not exceed {settings.MAX_UPLOAD_SIZE / (1024*1024)} MB.')
    
    def save(self, *args, **kwargs):
        """Clean and save the image."""
        self.clean()
        super().save(*args, **kwargs)


