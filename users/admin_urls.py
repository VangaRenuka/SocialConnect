from django.urls import path
from . import views

app_name = 'admin_users'

urlpatterns = [
    # Admin user management endpoints
    path('users/', views.AdminUserListView.as_view(), name='admin-user-list'),
    path('users/<int:pk>/', views.AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('users/<int:user_id>/deactivate/', views.AdminUserDeactivateView.as_view(), name='admin-user-deactivate'),
    path('stats/', views.AdminStatsView.as_view(), name='admin-stats'),
]


