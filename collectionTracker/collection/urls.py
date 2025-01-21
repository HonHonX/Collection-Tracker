from django.urls import path
from . import views
from integration.ticketmaster_query import fetch_artist_events

urlpatterns = [
    path('home/', views.home_view, name='index'),
    path('search/', views.artist_search, name="artist_search"),
    path('search/<str:artist_name>/', views.artist_search, name="artist_search"),
    path('artist_overview/<str:artist_id>/', views.artist_overview, name='artist_overview'),
    path('follow_artist/', views.follow_artist, name='follow_artist'),
    path('overview/<str:list_type>/', views.list_overview, name='list_overview'),
    path("manage_album/<str:list_type>/<str:action>/", views.manage_album, name="manage_album"),
    path("album/<str:album_id>/", views.AlbumDetail.as_view(), name="album_detail"),
    path("artist_detail/<str:artist_id>/", views.artist_detail, name="artist_detail"), 
    path('album-carousel/', views.album_carousel, name='album_carousel'),
    path('fetch-artist-events/<str:artist_name>/', fetch_artist_events, name='fetch_artist_events'),  
    path('fetch-recommendations/', views.get_recommendations, name="get_recommendations"),
    path('reload-recommendations/', views.reload_recommendations, name='reload_recommendations'),
]
