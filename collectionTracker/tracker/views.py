import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import subprocess
import logging

# Configure logger
logger = logging.getLogger(__name__)

# Retrieving credentials from .env
client_id = config('SPOTIFY_CLIENT_ID')
client_secret = config('SPOTIFY_CLIENT_SECRET')

# Authentication through Spotify API
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Create your views here.

# View for the landing page
def index(request):
    return HttpResponse("Neue Testseite unter /search 👩‍💻✨ woo")

# View for searching artist and displaying albums
def artist_search(request):
    albums = []
    error = None
    artist_photo_url = None
    artist_info = {}  # Initialize artist_info as empty
    latest_album = None

    if request.method == 'POST':
        artist_name = request.POST.get('artist_name')
        
        try:
            # Search by name → Spotify API
            result = sp.search(q=artist_name, type='artist')
            
            if len(result['artists']['items']) == 0:  # List empty
                error = f"Artist {artist_name} not found!"
            else:
                # Get artist's Spotify ID and image
                artist_info = result['artists']['items'][0]
                artist_id = artist_info['id']
                artist_photo_url = artist_info['images'][0]['url'] if artist_info['images'] else None

                # Get all albums for the artist using the artist ID
                album_results = sp.artist_albums(artist_id=artist_id)
                
                # Sort albums by release date
                sorted_albums = sorted(
                    album_results['items'],
                    key=lambda x: x['release_date'],
                    reverse=True  # Set to True if you want latest albums first
                )

                # Count total number of albums
                total_albums = len(sorted_albums)

                for album in sorted_albums:
                    # Fetch album details including the cover image
                    albums.append({
                        'name': album['name'],
                        'release_date': album['release_date'],
                        'total_tracks': album['total_tracks'],
                        'album_type': album['album_type'], 
                        'url': album['external_urls']['spotify'],
                        'image_url': album['images'][0]['url'] if album['images'] else None,
                        'spotify_id': album['id'],
                    })

                # Add artist info to the context (you can choose which fields to include)
                artist_info = {
                    'name': artist_info['name'],
                    'genres': artist_info['genres'],  # List of genres
                    'popularity': artist_info['popularity'],  # Popularity score
                    'total_albums': total_albums  # Total number of albums
                }

                # The first album in the sorted list is the latest
                if sorted_albums:
                    latest_album = sorted_albums[0]

        except Exception as e:
            error = str(e)  # Capture error message

        # Add a fallback if 'name' is not in artist_info
        artist_name = artist_info.get('name', 'Unknown Artist')  # Fallback to 'Unknown Artist'

        # Pass albums, artist info, artist photo, and error message to the template
        return render(request, 'tracker/artist_overview.html', {
            'albums': albums,
            'artist_name': artist_name,
            'artist_photo_url': artist_photo_url,
            'error': error,
            'artist_info': artist_info,
            'latest_album': latest_album,
        })
    
    return render(request, 'tracker/artist_search.html', {
        'artist_name': request.POST.get('artist_name', ''),
        'error': error,
    })
