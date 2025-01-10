import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.db import transaction
from collection.models import Artist, Album, UserAlbumCollection, UserAlbumWishlist, UserAlbumBlacklist, UserFollowedArtists  # Import the model
import json
from integration.discogs_query import get_more_artist_data, get_more_album_data

# Retrieving credentials from .env
client_id = config('SPOTIFY_CLIENT_ID')
client_secret = config('SPOTIFY_CLIENT_SECRET')

# Authentication through Spotify API
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


# View for searching artist and displaying albums
def get_artist_data(artist_name, user):
    albums = []
    error = None
    artist_photo_url = None
    artist_info = {}
    latest_album = None
    user_album_ids = []
    user_wishlist_ids = [] 
    user_blacklist_ids = []
    user_followed_artist_ids = []
    collection_count = 0 
    wishlist_count = 0
    blacklist_count = 0
    artist = None  # Initialize artist variable

    try:
        # Search by name → Spotify API
        result = sp.search(q=artist_name, type='artist')

        if len(result['artists']['items']) == 0:  # List empty
            error = f"Artist {artist_name} not found!"
        else:
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
                'id': artist_info['id'],  # Spotify ID
                'name': artist_info['name'],
                'genres': artist_info['genres'],  # List of genres
                'popularity': artist_info['popularity'],  # Popularity score
                'total_albums': total_albums  # Total number of albums
            }

            # The first album in the sorted list is the latest
            if sorted_albums:
                latest_album = sorted_albums[0]

            # Save artist and albums to the database
            with transaction.atomic():
                artist, created = Artist.objects.get_or_create(
                    id=artist_info['id'],
                    defaults={
                        'name': artist_info['name'],
                        'photo_url': artist_photo_url,
                        'popularity': artist_info['popularity'],
                    }
                )
                if created:
                    artist.set_genres(artist_info['genres'])
                    # Fetch more artist data from Discogs
                    more_artist_data = get_more_artist_data(artist_info['id'],artist_info['name'], user)
                    artist.discogs_id = more_artist_data.get('discogs_id')
                    artist.profile = more_artist_data.get('profile')
                    artist.aliases = more_artist_data.get('aliases')
                    artist.members = more_artist_data.get('members')
                    artist.urls = more_artist_data.get('urls')
                    artist.save()
                    # Refresh the artist object to get the updated data
                    artist.refresh_from_db()

                for album in sorted_albums:
                    album_instance, created = Album.objects.get_or_create(
                        id=album['id'],
                        defaults={
                            'name': album['name'],
                            'album_type': album['album_type'],
                            'release_date': album['release_date'],
                            'image_url': album['images'][0]['url'] if album['images'] else None,
                            'artist': artist,
                        }
                    )
                    if created: 
                        print(f"Album {album_instance.name} by {album_instance.artist.name} with the id {album_instance.id} created.")
                        more_album_data = get_more_album_data(album_instance.id, album_instance.name, album_instance.artist.name, user)
                        print(f"More album data: {more_album_data}")
                        album_instance.discogs_id = more_album_data.get('discogs_id')
                        album_instance.genres = more_album_data.get('genres', [])
                        album_instance.styles = more_album_data.get('styles', [])
                        album_instance.tracklist = more_album_data.get('tracklist', [])
                        album_instance.labels = more_album_data.get('labels', [])
                        album_instance.formats = more_album_data.get('formats', [])
                        # album_instance.lowest_price = more_album_data.get('lowest_price')
                        # album_instance.current_price = more_album_data.get('current_price')
                        # album_instance.highest_price = more_album_data.get('highest_price')
                        album_instance.save()
                        # Refresh the artist object to get the updated data
                        album_instance.refresh_from_db()

            # Get the list of user albums (user_album_ids), blacklist (user_blacklist_ids) and wishlist (user_wishlist_ids)
            if user.is_authenticated:
                # Get albums in the user's collection
                user_album_ids = list(
                    UserAlbumCollection.objects.filter(user=user)
                    .values_list('album__id', flat=True)
                )

                # Get albums in the user's wishlist
                user_wishlist_ids = list(
                    UserAlbumWishlist.objects.filter(user=user)
                    .values_list('album__id', flat=True)
                )

                # Get albums in the user's blacklist
                user_blacklist_ids = list(
                    UserAlbumBlacklist.objects.filter(user=user)
                    .values_list('album__id', flat=True)
                )

                # Get followed artists
                user_followed_artist_ids = list(
                    UserFollowedArtists.objects.filter(user=user)
                    .values_list('artist__id', flat=True)
                )

                # Calculate counts for collection, wishlist, and blacklist
                collection_count = sum(1 for album in sorted_albums if album['id'] in user_album_ids)
                wishlist_count = sum(1 for album in sorted_albums if album['id'] in user_wishlist_ids)
                blacklist_count = sum(1 for album in sorted_albums if album['id'] in user_blacklist_ids)

    except Exception as e:
        error = str(e)

    return {
        'albums': albums,
        'artist': artist,
        'artist_name': artist_info.get('name', 'Unknown Artist'),
        'artist_photo_url': artist_photo_url,
        'error': error,
        'artist_info': artist_info,
        'latest_album': latest_album,
        'user_album_ids': user_album_ids,
        'user_wishlist_ids': user_wishlist_ids,
        'user_blacklist_ids': user_blacklist_ids,
        'collection_count': collection_count,
        'wishlist_count': wishlist_count,
        'blacklist_count': blacklist_count,
        'user_followed_artist_ids': user_followed_artist_ids,
    }