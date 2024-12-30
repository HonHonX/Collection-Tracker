from django.urls import path
from . import views

urlpatterns = [
    path("", views.album_overview, name="user_album_collection"),
    path('my_collection/', views.album_overview, name='user_album_collection'),
    path("album_overview/", views.album_overview, name="album_overview"),
    path('album/<str:album_id>/', views.AlbumDetail.as_view(), name='album_detail'),
    path("add_album/", views.add_album_to_collection, name="add_album"),
    path("remove_album/", views.remove_album_from_collection, name="remove_album"),
    path('album/<str:album_id>/save_description/', views.save_description, name='save_description'),
    path("add_album_to_wishlist/", views.add_album_to_wishlist, name="add_album_to_wishlist"),
    path("remove_album_from_wishlist/", views.remove_album_from_wishlist, name="remove_album_from_wishlist"),
    path('wishlist/', views.wishlist_overview, name='wishlist_overview'),
    path('blacklist/', views.blacklist_overview, name='blacklist_overview'),
    path("add_album_to_blacklist/", views.add_album_to_blacklist, name="add_album_to_blacklist"),
    path("remove_album_from_blacklist/", views.remove_album_from_blacklist, name="remove_album_from_blacklist"),
]