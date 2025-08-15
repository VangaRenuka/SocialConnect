from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with extended functionality."""
    
    # Role choices
    ROLE_CHOICES = [
        ('user', 'User'),
        ('admin', 'Admin'),
    ]
    
    # Profile visibility choices
    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
        ('followers_only', 'Followers Only'),
    ]
    
    # Override email field to make it unique
    email = models.EmailField(unique=True, blank=False, null=False)
    
    # Username validation (3-30 chars, alphanumeric + underscore)
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]{3,30}$',
                message='Username must be 3-30 characters long and contain only letters, numbers, and underscores.'
            )
        ]
    )
    
    # Role field
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='user'
    )
    
    # Profile fields
    bio = models.CharField(max_length=160, blank=True)
    avatar_url = models.URLField(blank=True)
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Profile visibility
    profile_visibility = models.CharField(
        max_length=20,
        choices=VISIBILITY_CHOICES,
        default='public'
    )
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Email verification
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.CharField(max_length=100, blank=True)
    email_verification_expires = models.DateTimeField(null=True, blank=True)
    
    # Password reset
    password_reset_token = models.CharField(max_length=100, blank=True)
    password_reset_expires = models.DateTimeField(null=True, blank=True)
    
    # Account status
    is_active = models.BooleanField(default=True)
    is_deactivated = models.BooleanField(default=False)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def followers_count(self):
        """Return the number of followers."""
        return self.followers_set.count()
    
    @property
    def following_count(self):
        """Return the number of users being followed."""
        return self.following_set.count()
    
    @property
    def posts_count(self):
        """Return the number of posts."""
        return self.posts.count()
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def can_view_profile(self, requesting_user):
        """Check if requesting user can view this profile."""
        if self.profile_visibility == 'public':
            return True
        elif self.profile_visibility == 'private':
            return requesting_user == self
        elif self.profile_visibility == 'followers_only':
            return requesting_user == self or self.followers_set.filter(follower=requesting_user).exists()
        return False


class Follow(models.Model):
    """Model for user follow relationships."""
    
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_set'
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers_set'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'follows'
        unique_together = ('follower', 'following')
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    
    def save(self, *args, **kwargs):
        """Prevent self-following."""
        if self.follower == self.following:
            raise ValueError("Users cannot follow themselves.")
        super().save(*args, **kwargs)

