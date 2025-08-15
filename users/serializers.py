from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, Follow
from django.utils import timezone


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm', 'first_name', 'last_name']
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs
    
    def create(self, validated_data):
        """Create a new user."""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    email_or_username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        """Validate user credentials."""
        email_or_username = attrs.get('email_or_username')
        password = attrs.get('password')
        
        if email_or_username and password:
            # Try to authenticate with email or username
            if '@' in email_or_username:
                user = authenticate(email=email_or_username, password=password)
            else:
                user = authenticate(username=email_or_username, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email_or_username and password.')


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile display."""
    
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'bio', 'avatar_url', 'website', 'location', 'profile_visibility',
            'followers_count', 'following_count', 'posts_count',
            'date_joined', 'last_login', 'is_following'
        ]
        read_only_fields = ['id', 'email', 'date_joined', 'last_login']
    
    def get_is_following(self, obj):
        """Check if current user is following this user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(
                follower=request.user,
                following=obj
            ).exists()
        return False


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'avatar_url', 'website', 'location', 'profile_visibility']
    
    def validate_bio(self, value):
        """Validate bio length."""
        if len(value) > 160:
            raise serializers.ValidationError('Bio must be 160 characters or less.')
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password."""
    
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs
    
    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset request."""
    
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation."""
    
    token = serializers.CharField()
    new_password = serializers.CharField(validators=[validate_password])
    new_password_confirm = serializers.CharField()
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs


class FollowSerializer(serializers.ModelSerializer):
    """Serializer for follow relationships."""
    
    follower = UserProfileSerializer(read_only=True)
    following = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserListSerializer(serializers.ModelSerializer):
    """Serializer for user listing (admin and search)."""
    
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'is_active', 'is_deactivated', 'date_joined',
            'followers_count', 'following_count', 'posts_count'
        ]
        read_only_fields = ['id', 'date_joined', 'followers_count', 'following_count', 'posts_count']


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for admin user updates."""
    
    class Meta:
        model = User
        fields = ['role', 'is_active', 'is_deactivated']
    
    def update(self, instance, validated_data):
        """Update user with admin privileges."""
        if 'is_deactivated' in validated_data and validated_data['is_deactivated']:
            validated_data['deactivated_at'] = timezone.now()
        return super().update(instance, validated_data)


