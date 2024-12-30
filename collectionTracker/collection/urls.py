from django.urls import path
from . import views

urlpatterns = [
    # Overview routes
    path("", views.album_overview, name="user_album_collection"),
    path("my_collection/", views.album_overview, name="user_album_collection"),
    path("album_overview/", views.album_overview, name="album_overview"),
    path("wishlist/", views.wishlist_overview, name="wishlist_overview"),
    path("blacklist/", views.blacklist_overview, name="blacklist_overview"),

    # Album detail
    path("album/<str:album_id>/", views.AlbumDetail.as_view(), name="album_detail"),

    # Manage albums (generic)
    path("manage_album/<str:list_type>/<str:action>/", views.manage_album, name="manage_album"),

    # Save description
    path("album/<str:album_id>/save_description/", views.save_description, name="save_description"),
]
