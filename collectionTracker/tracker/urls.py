from django.urls import path

from . import views

urlpatterns = [
    path("", views.artist_search, name="artist_search"),
    path('get_user_progress/', views.get_user_progress, name='get_user_progress'),
]