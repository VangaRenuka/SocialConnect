from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include([
        path('auth/', include('users.urls')),
        path('users/', include('users.urls')),
        path('posts/', include('posts.urls')),
        path('feed/', include('feed.urls')),
        path('notifications/', include('notifications.urls')),
        path('admin/', include('users.admin_urls')),
    ])),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

