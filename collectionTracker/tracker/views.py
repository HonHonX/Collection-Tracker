import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import os
import subprocess
import logging
from django.contrib.auth.decorators import login_required
from collection.models import UserAlbumCollection, UserAlbumWishlist, UserAlbumBlacklist

# Configure logger
logger = logging.getLogger(__name__)

# Retrieving credentials from .env
client_id = config('SPOTIFY_CLIENT_ID')
client_secret = config('SPOTIFY_CLIENT_SECRET')

# Authentication through Spotify API
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Create your views here.

# View for searching artist and displaying albums
def artist_search(request):
    albums = []
    error = None
    artist_photo_url = None
    artist_info = {}
    latest_album = None
    user_album_ids = []  # Initialize the variable for user album IDs
    user_wishlist_ids = []  # Initialize the variable for user wishlist IDs
    user_blacklist_ids = []  # Initialize the variable for user blacklist IDs

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

                # Add album details to the albums list
                for album in sorted_albums:
                    albums.append({
                        'name': album['name'],
                        'release_date': album['release_date'],
                        'total_tracks': album['total_tracks'],
                        'album_type': album['album_type'], 
                        'url': album['external_urls']['spotify'],
                        'image_url': album['images'][0]['url'] if album['images'] else None,
                        'spotify_id': album['id'],
                    })

                # Add artist info to the context
                artist_info = {
                    'name': artist_info['name'],
                    'genres': artist_info['genres'],  # List of genres
                    'popularity': artist_info['popularity'],  # Popularity score
                    'total_albums': total_albums  # Total number of albums
                }

                # The first album in the sorted list is the latest
                if sorted_albums:
                    latest_album = sorted_albums[0]

                # Get the list of user albums (user_album_ids), blacklist (user_blacklist_ids) and wishlist (user_wishlist_ids)
                if request.user.is_authenticated:
                    # Get albums in the user's collection
                    user_album_ids = list(
                        UserAlbumCollection.objects.filter(user=request.user)
                        .values_list('album__id', flat=True)
                    )

                    # Get albums in the user's wishlist
                    user_wishlist_ids = list(
                        UserAlbumWishlist.objects.filter(user=request.user)
                        .values_list('album__id', flat=True)
                    )

                    # Get albums in the user's blacklist
                    user_blacklist_ids = list(
                        UserAlbumBlacklist.objects.filter(user=request.user)
                        .values_list('album__id', flat=True)
                    )

                    # Calculate counts for collection, wishlist, and blacklist
                    collection_count = sum(1 for album in sorted_albums if album['id'] in user_album_ids)
                    wishlist_count = sum(1 for album in sorted_albums if album['id'] in user_wishlist_ids)
                    blacklist_count = sum(1 for album in sorted_albums if album['id'] in user_blacklist_ids)

        except Exception as e:
            error = str(e)

        # Add a fallback if 'name' is not in artist_info
        artist_name = artist_info.get('name', 'Unknown Artist')  # Fallback to 'Unknown Artist'

        # Pass albums, artist info, artist photo, error message, user_album_ids,user_wishlist_ids and user_blacklist_ids to the template
        return render(request, 'tracker/artist_overview.html', {
            'albums': albums,
            'artist_name': artist_name,
            'artist_photo_url': artist_photo_url,
            'error': error,
            'artist_info': artist_info,
            'latest_album': latest_album,
            'user_album_ids': user_album_ids,  # Include user_album_ids in the context
            'user_wishlist_ids': user_wishlist_ids,  # Include user_wishlist_ids in the context
            'user_blacklist_ids': user_blacklist_ids,  # Include user_wishlist_ids in the context
            'collection_count': collection_count,  # Include collection_count
            'wishlist_count': wishlist_count,  # Include wishlist_count
            'blacklist_count': blacklist_count,  # Include blacklist_count
        })
    
    return render(request, 'tracker/artist_search.html', {
        'artist_name': request.POST.get('artist_name', ''),
        'error': error,
    })

@login_required
@csrf_exempt
def update_album_status(request):
    if request.method == "POST":
        album_id = request.POST.get("album_id")
        action = request.POST.get("action")
        album = get_object_or_404(Album, id=album_id)

        if action == "add_to_collection":
            UserAlbumCollection.objects.get_or_create(user=request.user, album=album)
        elif action == "remove_from_collection":
            UserAlbumCollection.objects.filter(user=request.user, album=album).delete()
        elif action == "add_to_wishlist":
            UserAlbumWishlist.objects.get_or_create(user=request.user, album=album)
        elif action == "remove_from_wishlist":
            UserAlbumWishlist.objects.filter(user=request.user, album=album).delete()
        elif action == "add_to_blacklist":
            UserAlbumBlacklist.objects.get_or_create(user=request.user, album=album)
        elif action == "remove_from_blacklist":
            UserAlbumBlacklist.objects.filter(user=request.user, album=album).delete()

        # Fetch updated progress
        progress = UserArtistProgress.objects.get(user=request.user, artist=album.artist)

        return JsonResponse({
            "collection_count": progress.collection_count,
            "wishlist_count": progress.wishlist_count,
            "collection_and_wishlist_count": progress.collection_and_wishlist_count,
            "blacklist_count": progress.blacklist_count,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
