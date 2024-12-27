from django.urls import path
from . import views

urlpatterns = [
    path("", views.album_overview, name="collection"),
    path('my_collection/', views.album_overview, name='user_album_collection'),
    path("album_overview/", views.album_overview, name="album_overview"),
    path("album_detail/<str:album_id>/", views.AlbumDetail.as_view(), name="album_detail"),
    path("add_album/", views.add_album_to_collection, name="add_album"),
    path("remove_album/", views.remove_album_from_collection, name="remove_album"),
]