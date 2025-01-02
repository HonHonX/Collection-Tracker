from django.urls import path
from . import views

urlpatterns = [
    path('', views.friends_view, name='friends_view'),
    path('confirm/<str:friend_email>/<str:sender_username>/', views.confirm_friend_request, name='confirm_friend_request'),
]
