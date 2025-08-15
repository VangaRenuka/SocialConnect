from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import secrets
import hashlib

from .models import User, Follow
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    UserProfileUpdateSerializer, PasswordChangeSerializer, PasswordResetSerializer,
    PasswordResetConfirmSerializer, FollowSerializer, UserListSerializer,
    AdminUserUpdateSerializer
)
from .permissions import IsOwnerOrReadOnly, IsAdminUser

User = get_user_model()


class UserRegistrationView(APIView):
    """User registration endpoint."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate email verification token
            token = secrets.token_urlsafe(32)
            user.email_verification_token = token
            user.email_verification_expires = timezone.now() + timezone.timedelta(hours=24)
            user.save()
            
            # Send verification email (in production, use Celery for async)
            try:
                send_mail(
                    'Verify your SocialConnect account',
                    f'Click this link to verify your account: {request.build_absolute_uri("/verify-email/")}?token={token}',
                    settings.EMAIL_HOST_USER,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                # Log error but don't fail registration
                print(f"Email sending failed: {e}")
            
            return Response({
                'message': 'User registered successfully. Please check your email to verify your account.',
                'user_id': user.id
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """User login endpoint."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Update last login
            user.last_login = timezone.now()
            user.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': UserProfileSerializer(user, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogoutView(APIView):
    """User logout endpoint."""
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordChangeView(APIView):
    """Change password endpoint."""
    
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """Password reset request endpoint."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                # Generate reset token
                token = secrets.token_urlsafe(32)
                user.password_reset_token = token
                user.password_reset_expires = timezone.now() + timezone.timedelta(hours=1)
                user.save()
                
                # Send reset email
                try:
                    send_mail(
                        'Reset your SocialConnect password',
                        f'Click this link to reset your password: {request.build_absolute_uri("/reset-password/")}?token={token}',
                        settings.EMAIL_HOST_USER,
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    print(f"Email sending failed: {e}")
                
                return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'message': 'Password reset email sent'}, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """Password reset confirmation endpoint."""
    
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            new_password = serializer.validated_data['new_password']
            
            try:
                user = User.objects.get(
                    password_reset_token=token,
                    password_reset_expires__gt=timezone.now()
                )
                
                user.set_password(new_password)
                user.password_reset_token = ''
                user.password_reset_expires = None
                user.save()
                
                return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'Invalid or expired token'}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view and update."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_object(self):
        """Get user profile by username or return current user."""
        username = self.kwargs.get('username')
        if username:
            try:
                user = User.objects.get(username=username)
                # Check if current user can view this profile
                if not user.can_view_profile(self.request.user):
                    raise User.DoesNotExist()
                return user
            except User.DoesNotExist:
                return None
        return self.request.user
    
    def get_serializer_class(self):
        """Use different serializer for updates."""
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer


class UserListView(generics.ListAPIView):
    """User list view for admin and search."""
    
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        queryset = User.objects.filter(is_active=True)
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(username__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        # Role filter (admin only)
        role = self.request.query_params.get('role', None)
        if role and self.request.user.is_admin():
            queryset = queryset.filter(role=role)
        
        return queryset.order_by('-date_joined')


class FollowUserView(APIView):
    """Follow/unfollow user endpoint."""
    
    def post(self, request, user_id):
        try:
            user_to_follow = User.objects.get(id=user_id, is_active=True)
            
            if user_to_follow == request.user:
                return Response({'error': 'Cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if already following
            if Follow.objects.filter(follower=request.user, following=user_to_follow).exists():
                return Response({'error': 'Already following this user'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Create follow relationship
            Follow.objects.create(follower=request.user, following=user_to_follow)
            
            return Response({'message': f'Successfully followed {user_to_follow.username}'}, status=status.HTTP_201_CREATED)
        
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UnfollowUserView(APIView):
    """Unfollow user endpoint."""
    
    def delete(self, request, user_id):
        try:
            user_to_unfollow = User.objects.get(id=user_id)
            
            # Check if following
            follow = Follow.objects.filter(follower=request.user, following=user_to_unfollow)
            if not follow.exists():
                return Response({'error': 'Not following this user'}, status=status.HTTP_400_BAD_REQUEST)
            
            follow.delete()
            
            return Response({'message': f'Successfully unfollowed {user_to_unfollow.username}'}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserFollowersView(generics.ListAPIView):
    """Get user followers."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            return User.objects.filter(following_set__following=user, is_active=True)
        except User.DoesNotExist:
            return User.objects.none()


class UserFollowingView(generics.ListAPIView):
    """Get users that a user is following."""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user_id = self.kwargs.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            return User.objects.filter(followers_set__follower=user, is_active=True)
        except User.DoesNotExist:
            return User.objects.none()


# Admin Views
class AdminUserListView(generics.ListAPIView):
    """Admin view for listing all users."""
    
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')


class AdminUserDetailView(generics.RetrieveUpdateAPIView):
    """Admin view for user details and updates."""
    
    serializer_class = AdminUserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    queryset = User.objects.all()


class AdminUserDeactivateView(APIView):
    """Admin view for deactivating users."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def post(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if user == request.user:
                return Response({'error': 'Cannot deactivate yourself'}, status=status.HTTP_400_BAD_REQUEST)
            
            user.is_deactivated = True
            user.deactivated_at = timezone.now()
            user.save()
            
            return Response({'message': f'User {user.username} deactivated successfully'}, status=status.HTTP_200_OK)
        
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class AdminStatsView(APIView):
    """Admin view for basic statistics."""
    
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        
        stats = {
            'total_users': User.objects.count(),
            'total_posts': 0,  # Will be updated when posts app is created
            'active_today': User.objects.filter(last_login__date=today).count(),
            'new_users_today': User.objects.filter(date_joined__date=today).count(),
        }
        
        return Response(stats, status=status.HTTP_200_OK)
