from django.urls import path
from . import views
from tracker.views import follow_artist  # Import the view

urlpatterns = [
    # Overview routes
    path("collection-overview/", views.album_overview, name="collection_overview"),
    path("wishlist-overview/", views.wishlist_overview, name="wishlist_overview"),
    path("blacklist-overview/", views.blacklist_overview, name="blacklist_overview"),

    # Album detail
    path("album/<str:album_id>/", views.AlbumDetail.as_view(), name="album_detail"),

    # Manage albums (generic)
    path("manage_album/<str:list_type>/<str:action>/", views.manage_album, name="manage_album"),

    # Save description
    path("album/<str:album_id>/save_description/", views.save_description, name="save_description"),

    # Follow artist
    path('follow_artist/', follow_artist, name='follow_artist'),
]
  