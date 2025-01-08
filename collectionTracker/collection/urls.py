from django.urls import path
from . import views

urlpatterns = [

    # Home route
    path('home/', views.home_view, name='index'),

    # Artist search
    path('search/', views.artist_search, name="artist_search"),

    # Artist overview
    path('artist/<str:artist_name>/', views.artist_overview, name='artist_overview'),

    # Follow artist
    path('follow_artist/', views.follow_artist, name='follow_artist'),

    # Overview route (generic)
    path('overview/<str:list_type>/', views.list_overview, name='list_overview'),

    # Manage albums (generic)
    path("manage_album/<str:list_type>/<str:action>/", views.manage_album, name="manage_album"),

    # Album detail
    path("album/<str:album_id>/", views.AlbumDetail.as_view(), name="album_detail"),
    
]
 