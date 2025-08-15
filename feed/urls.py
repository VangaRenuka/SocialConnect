from django.urls import path
from . import views

app_name = 'feed'

urlpatterns = [
    # Main personalized feed
    path('', views.PersonalizedFeedView.as_view(), name='personalized-feed'),
    
    # Trending feed
    path('trending/', views.TrendingFeedView.as_view(), name='trending-feed'),
    
    # Category feeds
    path('category/<str:category>/', views.CategoryFeedView.as_view(), name='category-feed'),
]


