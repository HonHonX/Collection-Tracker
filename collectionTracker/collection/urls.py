from django.urls import path
from . import views

urlpatterns = [
    path("", views.album_overview.as_view()),
    path("album_overview/", views.album_overview.as_view(), name="album_overview"),
    path("album_detail/", views.album_detail.as_view(), name="album_detail"),
    path("add_album/", views.add_album_to_collection, name='add_album'),
    path('my_collection/', views.user_album_collection, name='user_album_collection'),
]