from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Notification endpoints
    path('', views.NotificationListView.as_view(), name='notification-list'),
    path('<int:pk>/', views.NotificationDetailView.as_view(), name='notification-detail'),
    path('<int:notification_id>/read/', views.NotificationMarkAsReadView.as_view(), name='notification-mark-read'),
    path('<int:notification_id>/archive/', views.NotificationArchiveView.as_view(), name='notification-archive'),
    path('<int:notification_id>/unarchive/', views.NotificationUnarchiveView.as_view(), name='notification-unarchive'),
    path('<int:notification_id>/delete/', views.NotificationDeleteView.as_view(), name='notification-delete'),
    
    # Bulk operations
    path('mark-all-read/', views.NotificationMarkAllAsReadView.as_view(), name='notification-mark-all-read'),
    
    # Statistics and preferences
    path('stats/', views.NotificationStatsView.as_view(), name='notification-stats'),
    path('preferences/', views.NotificationPreferenceView.as_view(), name='notification-preferences'),
    path('test/', views.NotificationTestView.as_view(), name='notification-test'),
    
    # Admin endpoints
    path('admin/', views.AdminNotificationListView.as_view(), name='admin-notification-list'),
    path('admin/<int:notification_id>/delete/', views.AdminNotificationDeleteView.as_view(), name='admin-notification-delete'),
]


