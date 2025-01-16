from django.urls import path
from . import views
from integration.ticketmaster_query import fetch_artist_events

urlpatterns = [

    # Home route
    path('home/', views.home_view, name='index'),

    # Artist search
    path('search/', views.artist_search, name="artist_search"),
    path('search/<str:artist_name>/', views.artist_search, name="artist_search"),

    # Artist overview
    path('artist_overview/<str:artist_id>/', views.artist_overview, name='artist_overview'),

    # Follow artist
    path('follow_artist/', views.follow_artist, name='follow_artist'),

    # Overview route (generic)
    path('overview/<str:list_type>/', views.list_overview, name='list_overview'),

    # Manage albums (generic)
    path("manage_album/<str:list_type>/<str:action>/", views.manage_album, name="manage_album"),

    # Album detail
    path("album/<str:album_id>/", views.AlbumDetail.as_view(), name="album_detail"),

    # Artist detail
    path("artist_detail/<str:artist_id>/", views.artist_detail, name="artist_detail"), 

    # Album carousel
    path('album-carousel/', views.album_carousel, name='album_carousel'),

    #Fetch artist events
    path('fetch-artist-events/<str:artist_name>/', fetch_artist_events, name='fetch_artist_events'),
    
]
 