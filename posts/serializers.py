from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Like, PostImage

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for nested objects."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'avatar_url']


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments."""
    
    author = UserBasicSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='author',
        write_only=True
    )
    
    class Meta:
        model = Comment
        fields = ['id', 'content', 'author', 'author_id', 'post', 'created_at', 'is_active']
        read_only_fields = ['id', 'created_at', 'is_active']
    
    def validate_content(self, value):
        """Validate comment content length."""
        if len(value) > 200:
            raise serializers.ValidationError('Comment must be 200 characters or less.')
        return value


class PostImageSerializer(serializers.ModelSerializer):
    """Serializer for post images."""
    
    class Meta:
        model = PostImage
        fields = ['id', 'image', 'uploaded_at']
        read_only_fields = ['id', 'uploaded_at']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for posts."""
    
    author = UserBasicSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='author',
        write_only=True
    )
    comments = CommentSerializer(many=True, read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_author = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'content', 'author', 'author_id', 'created_at', 'updated_at',
            'image_url', 'category', 'is_active', 'like_count', 'comment_count',
            'comments', 'images', 'is_liked', 'is_author'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'like_count', 'comment_count']
    
    def validate_content(self, value):
        """Validate post content length."""
        if len(value) > 280:
            raise serializers.ValidationError('Post content must be 280 characters or less.')
        return value
    
    def get_is_liked(self, obj):
        """Check if current user has liked this post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_is_author(self, obj):
        """Check if current user is the author of this post."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.author == request.user
        return False


class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts."""
    
    class Meta:
        model = Post
        fields = ['content', 'image_url', 'category']
    
    def validate_content(self, value):
        """Validate post content length."""
        if len(value) > 280:
            raise serializers.ValidationError('Post content must be 280 characters or less.')
        return value


class PostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating posts."""
    
    class Meta:
        model = Post
        fields = ['content', 'image_url', 'category']
    
    def validate_content(self, value):
        """Validate post content length."""
        if len(value) > 280:
            raise serializers.ValidationError('Post content must be 280 characters or less.')
        return value


class LikeSerializer(serializers.ModelSerializer):
    """Serializer for likes."""
    
    user = UserBasicSerializer(read_only=True)
    post = PostSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['id', 'created_at']


class PostDetailSerializer(PostSerializer):
    """Detailed post serializer with full comment information."""
    
    comments = CommentSerializer(many=True, read_only=True)
    images = PostImageSerializer(many=True, read_only=True)
    
    class Meta(PostSerializer.Meta):
        pass


class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments."""
    
    class Meta:
        model = Comment
        fields = ['content']
    
    def validate_content(self, value):
        """Validate comment content length."""
        if len(value) > 200:
            raise serializers.ValidationError('Comment must be 200 characters or less.')
        return value


class CommentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating comments."""
    
    class Meta:
        model = Comment
        fields = ['content']
    
    def validate_content(self, value):
        """Validate comment content length."""
        if len(value) > 200:
            raise serializers.ValidationError('Comment must be 200 characters or less.')
        return value

