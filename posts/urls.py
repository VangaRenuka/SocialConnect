from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Post endpoints
    path('', views.PostListView.as_view(), name='post-list'),
    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    
    # Post interaction endpoints
    path('<int:post_id>/like/', views.PostLikeView.as_view(), name='post-like'),
    path('<int:post_id>/unlike/', views.PostUnlikeView.as_view(), name='post-unlike'),
    path('<int:post_id>/like-status/', views.PostLikeStatusView.as_view(), name='post-like-status'),
    
    # Comment endpoints
    path('<int:post_id>/comments/', views.CommentListView.as_view(), name='comment-list'),
    path('comments/<int:pk>/', views.CommentDetailView.as_view(), name='comment-detail'),
    
    # User posts
    path('user/<str:username>/', views.UserPostsView.as_view(), name='user-posts'),
    
    # Admin endpoints
    path('admin/', views.AdminPostListView.as_view(), name='admin-post-list'),
    path('admin/<int:post_id>/delete/', views.AdminPostDeleteView.as_view(), name='admin-post-delete'),
    path('admin/comments/', views.AdminCommentListView.as_view(), name='admin-comment-list'),
    path('admin/comments/<int:comment_id>/delete/', views.AdminCommentDeleteView.as_view(), name='admin-comment-delete'),
]

