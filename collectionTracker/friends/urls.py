from django.urls import path
from . import views

urlpatterns = [
    # URL pattern for the friends view
    path('', views.friends_view, name='friends_view'),
    
    # URL pattern for confirming a friend request
    path('confirm/<str:friend_email>/<str:sender_username>/', views.confirm_friend_request, name='confirm_friend_request'),
    
    # URL pattern for viewing a friend's wishlist
    path('<str:username>/wishlist/', views.friend_wishlist, name='friend_wishlist'),
    
    # URL pattern for viewing a friend's collection
    path('<str:username>/collection/', views.friend_collection, name='friend_collection'),
    
    # URL pattern for viewing a shared user's wishlist
    path('share/<str:token>/wishlist/', views.shared_user_wishlist, name='shared_user_wishlist'),
    
    # URL pattern for viewing a shared user's collection
    path('share/<str:token>/collection/', views.shared_user_collection, name='shared_user_collection'),
    
    # URL pattern for generating a token
    path('generate_token/', views.generate_token, name='generate_token'),
]
