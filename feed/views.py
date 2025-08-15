from rest_framework import generics, permissions
from rest_framework.response import Response
from django.db.models import Q, F
from django.contrib.auth import get_user_model

from posts.models import Post
from posts.serializers import PostSerializer
from users.models import Follow

User = get_user_model()


class PersonalizedFeedView(generics.ListAPIView):
    """Personalized feed showing posts from followed users and own posts."""
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Get users that the current user follows
        following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
        
        # Get posts from followed users + own posts
        queryset = Post.objects.filter(
            Q(author__in=following_users) | Q(author=user),
            is_active=True
        ).select_related('author').prefetch_related('likes', 'comments')
        
        # Order by creation date (newest first)
        queryset = queryset.order_by('-created_at')
        
        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        # Author filter (for specific user's posts in feed)
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__username=author)
        
        # Search functionality within feed
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(content__icontains=search) |
                Q(author__username__icontains=search)
            )
        
        return queryset
    
    def get(self, request, *args, **kwargs):
        """Get personalized feed with additional context."""
        queryset = self.get_queryset()
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add feed metadata
            response.data['feed_info'] = {
                'total_posts': queryset.count(),
                'user_following_count': Follow.objects.filter(follower=request.user).count(),
                'feed_type': 'personalized'
            }
            
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TrendingFeedView(generics.ListAPIView):
    """Trending feed based on engagement (likes and comments)."""
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get trending posts based on engagement."""
        queryset = Post.objects.filter(
            is_active=True
        ).select_related('author').prefetch_related('likes', 'comments')
        
        # Order by engagement (likes + comments)
        queryset = queryset.annotate(
            engagement_score=F('like_count') + F('comment_count')
        ).order_by('-engagement_score', '-created_at')
        
        # Time filter (last 7 days for trending)
        from django.utils import timezone
        from datetime import timedelta
        
        days = self.request.query_params.get('days', 7)
        cutoff_date = timezone.now() - timedelta(days=int(days))
        queryset = queryset.filter(created_at__gte=cutoff_date)
        
        # Category filter
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category=category)
        
        return queryset
    
    def get(self, request, *args, **kwargs):
        """Get trending feed with additional context."""
        queryset = self.get_queryset()
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add feed metadata
            response.data['feed_info'] = {
                'total_posts': queryset.count(),
                'feed_type': 'trending',
                'time_period': self.request.query_params.get('days', 7)
            }
            
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class CategoryFeedView(generics.ListAPIView):
    """Feed filtered by specific category."""
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get posts by category."""
        category = self.kwargs.get('category')
        
        if category not in dict(Post.CATEGORY_CHOICES):
            return Post.objects.none()
        
        queryset = Post.objects.filter(
            category=category,
            is_active=True
        ).select_related('author').prefetch_related('likes', 'comments')
        
        # Order by creation date
        queryset = queryset.order_by('-created_at')
        
        # Author filter
        author = self.request.query_params.get('author', None)
        if author:
            queryset = queryset.filter(author__username=author)
        
        return queryset
    
    def get(self, request, *args, **kwargs):
        """Get category feed with additional context."""
        queryset = self.get_queryset()
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            
            # Add feed metadata
            response.data['feed_info'] = {
                'category': self.kwargs.get('category'),
                'total_posts': queryset.count(),
                'feed_type': 'category'
            }
            
            return response
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
