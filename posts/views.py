from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.contrib.auth import get_user_model

from .models import Post, Comment, Like
from .serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer, PostDetailSerializer,
    CommentSerializer, CommentCreateSerializer, CommentUpdateSerializer,
    LikeSerializer
)
from users.permissions import IsOwnerOrAdmin

User = get_user_model()


class PostListView(generics.ListCreateAPIView):
    """List all posts with pagination and create new posts."""
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return PostCreateSerializer
        return PostSerializer
    
    def perform_create(self, serializer):
        """Set the author to the current user."""
        serializer.save(author=self.request.user)
    
    def get_queryset(self):
        queryset = Post.objects.filter(is_active=True).select_related('author')
        
        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Author filter
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__username=author)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(content__icontains=search) |
                Q(author__username__icontains=search)
            )
        
        return queryset


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a post."""
    
    serializer_class = PostDetailSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = Post.objects.filter(is_active=True).select_related('author')
    
    def get_serializer_class(self):
        """Use different serializer for updates."""
        if self.request.method in ['PUT', 'PATCH']:
            return PostUpdateSerializer
        return PostDetailSerializer


class PostLikeView(APIView):
    """Like a post."""
    
    def post(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_active=True)
        
        # Check if already liked
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response({'error': 'Post already liked'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create like
        Like.objects.create(user=request.user, post=post)
        
        return Response({'message': 'Post liked successfully'}, status=status.HTTP_201_CREATED)


class PostUnlikeView(APIView):
    """Unlike a post."""
    
    def delete(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_active=True)
        
        # Check if liked
        like = Like.objects.filter(user=request.user, post=post)
        if not like.exists():
            return Response({'error': 'Post not liked'}, status=status.HTTP_400_BAD_REQUEST)
        
        like.delete()
        
        return Response({'message': 'Post unliked successfully'}, status=status.HTTP_200_OK)


class PostLikeStatusView(APIView):
    """Check if user has liked a post."""
    
    def get(self, request, post_id):
        post = get_object_or_404(Post, id=post_id, is_active=True)
        
        is_liked = Like.objects.filter(user=request.user, post=post).exists()
        
        return Response({
            'post_id': post_id,
            'is_liked': is_liked,
            'like_count': post.like_count
        })


class CommentListView(generics.ListCreateAPIView):
    """List comments for a post and create new comments."""
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        """Use different serializer for creation."""
        if self.request.method == 'POST':
            return CommentCreateSerializer
        return CommentSerializer
    
    def perform_create(self, serializer):
        """Set the author to the current user."""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id, is_active=True)
        serializer.save(author=self.request.user, post=post)
    
    def get_queryset(self):
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, id=post_id, is_active=True)
        return Comment.objects.filter(post=post, is_active=True).select_related('author')


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a comment."""
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    queryset = Comment.objects.filter(is_active=True).select_related('author', 'post')
    
    def get_serializer_class(self):
        """Use different serializer for updates."""
        if self.request.method in ['PUT', 'PATCH']:
            return CommentUpdateSerializer
        return CommentSerializer


class UserPostsView(generics.ListAPIView):
    """Get posts by a specific user."""
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username, is_active=True)
        
        # Check if current user can view this user's posts
        if not user.can_view_profile(self.request.user):
            return Post.objects.none()
        
        return Post.objects.filter(author=user, is_active=True).select_related('author')


# Admin Views
class AdminPostListView(generics.ListAPIView):
    """Admin view for listing all posts."""
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only admins can access this view
        if not self.request.user.is_admin():
            return Post.objects.none()
        
        queryset = Post.objects.all().select_related('author')
        
        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Status filter
        status_filter = self.request.query_params.get('status', None)
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset


class AdminPostDeleteView(APIView):
    """Admin view for deleting any post."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, post_id):
        # Only admins can delete posts
        if not request.user.is_admin():
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        post = get_object_or_404(Post, id=post_id)
        post.delete()
        
        return Response({'message': 'Post deleted successfully'}, status=status.HTTP_200_OK)


class AdminCommentListView(generics.ListAPIView):
    """Admin view for listing all comments."""
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Only admins can access this view
        if not self.request.user.is_admin():
            return Comment.objects.none()
        
        return Comment.objects.all().select_related('author', 'post')


class AdminCommentDeleteView(APIView):
    """Admin view for deleting any comment."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, comment_id):
        # Only admins can delete comments
        if not request.user.is_admin():
            return Response({'error': 'Admin access required'}, status=status.HTTP_403_FORBIDDEN)
        
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        
        return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_200_OK)

