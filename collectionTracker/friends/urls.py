from django.urls import path
from . import views

urlpatterns = [
    path('', views.friends_view, name='friends_view'),
    path('confirm/<str:friend_email>/<str:sender_username>/', views.confirm_friend_request, name='confirm_friend_request'),
    path('<str:username>/wishlist/', views.user_wishlist, name='user_wishlist'),
    path('<str:username>/collection/', views.user_collection, name='user_collection'),
    path('share/<str:token>/wishlist/', views.shared_user_wishlist, name='shared_user_wishlist'),
    path('share/<str:token>/collection/', views.shared_user_collection, name='shared_user_collection'),
    path('generate_token/', views.generate_token, name='generate_token'),
]
