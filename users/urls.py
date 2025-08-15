from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    path('password/reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('password/reset/confirm/', views.PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
    
    # User profile endpoints
    path('me/', views.UserProfileView.as_view(), name='user-profile'),
    path('<str:username>/', views.UserProfileView.as_view(), name='user-profile-detail'),
    path('', views.UserListView.as_view(), name='user-list'),
    
    # Follow system endpoints
    path('<int:user_id>/follow/', views.FollowUserView.as_view(), name='follow-user'),
    path('<int:user_id>/unfollow/', views.UnfollowUserView.as_view(), name='unfollow-user'),
    path('<int:user_id>/followers/', views.UserFollowersView.as_view(), name='user-followers'),
    path('<int:user_id>/following/', views.UserFollowingView.as_view(), name='user-following'),
]


