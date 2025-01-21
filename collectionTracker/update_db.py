import os
import sys

# Add the root directory of the project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collectionTracker.settings')

import django
django.setup()

from django.core.wsgi import get_wsgi_application
from stats.models import AlbumPricePrediction
from stats.views import save_album_price_predictions
from collection.models import Album, Artist, User
from integration.discogs_query import update_album_price
from integration.spotify_query import get_artist_data
from integration.lastfm_query import artist_recommendations
from utils.stats_helpers import calculate_top_genres
from collection.models import RecommendedArtist, UserFollowedArtists
import time
import requests 
import json

application = get_wsgi_application()

def fetch_and_save_recommendations(user):
    top_genres = calculate_top_genres(user)
    genres = [genre.name for genre in top_genres]
    
    try:
        response = artist_recommendations(genres)
        data = response.json() if isinstance(response, requests.Response) else json.loads(response.content)
        artists = data.get('artists', [])
        error = None

        artist_objects = []
        for name in artists:
            artist_data = get_artist_data(name, user)
            artist_objects.append(artist_data['artist'])

        followed_artist_ids = UserFollowedArtists.objects.filter(user=user).values_list('artist_id', flat=True)
        recommended_artists = [
            artist for artist in artist_objects if artist.id not in followed_artist_ids
        ]

        RecommendedArtist.objects.filter(user=user).delete()
        for artist in recommended_artists:
            RecommendedArtist.objects.create(user=user, artist=artist)

        return RecommendedArtist.objects.filter(user=user)

    except requests.exceptions.RequestException as e:
        return []

def update_recommendations():
    users = User.objects.all()
    for user in users:
        fetch_and_save_recommendations(user)

albums = Album.objects.all()
for album in albums:
    success = update_album_price(album.id)
    if success:
        print(f"Updated price for album {album.name} (ID: {album.id})")
    else:
        print(f"Failed to update price for album {album.name} (ID: {album.id})")
    
    time.sleep(1.2)  

updated_albums = Album.objects.filter(dailyalbumprice__isnull=False).distinct()
for album in updated_albums:
    save_album_price_predictions(None, album.id)
    print(f"Saved price predictions for album {album.name} (ID: {album.id})")

artistList = Artist.objects.all()
for artist in artistList:
    artist_name = artist.name  
    get_artist_data(user=None,artist_name=artist_name) 
    print(f"Updated artist data for {artist.name} (ID: {artist.id})")

update_recommendations()

