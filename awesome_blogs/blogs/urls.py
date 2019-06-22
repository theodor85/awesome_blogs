from django.urls import path

from .views import (FeedView, UserPostsView, MyPostsView, 
    AddPostView, DetailPostView, SubscriptionsView,
    )


app_name = 'blogs'
urlpatterns = [
    path('feed/', FeedView.as_view(), name='feed'),
    path('<str:username>/', UserPostsView.as_view(), name='userposts'),
    path('my/', MyPostsView.as_view(), name='myposts'),
    path('add/', AddPostView.as_view(), name='add'),
    path('detail/<int:pk>/', DetailPostView.as_view(), name='detail'),
    path('subscriptions/', SubscriptionsView.as_view(), name='subscriptions'),
]