import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from decouple import config
from django.db import transaction
from collection.models import Artist, Album, UserAlbumCollection, UserAlbumWishlist, UserAlbumBlacklist, UserFollowedArtists
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Retrieving credentials from .env
client_id = config('SPOTIFY_CLIENT_ID')
client_secret = config('SPOTIFY_CLIENT_SECRET')

# Authentication through Spotify API
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)

def convert_to_valid_date_format(date_value):
    """
    Converts a date string to a valid date format.

    Parameters:
    date_value (str): The date string to convert.

    Returns:
    str: The converted date string in the format 'YYYY-MM-DD'.
    """
    try:
        if not date_value:
            # If there is no release date at all, set year to 1900
            valid_date = "1900-01-01"
        elif len(date_value) == 4:
            # If only a year is provided, set month and day to 01
            valid_date = datetime.strptime(date_value, "%Y").strftime("%Y-01-01")
        else:
            # Assuming date_value is a string like "2018-12-31"
            valid_date = datetime.strptime(date_value, "%Y-%m-%d").strftime("%Y-%m-%d")
        return valid_date
    except ValueError:
        # Handle the case where the date_value is not in the expected format
        print(f"Invalid date format for value: {date_value}")
        return None        

def get_artist_data(artist_name, user):
    """
    Retrieves artist data and their albums from Spotify and updates the database.

    Parameters:
    artist_name (str): The name of the artist to search for.
    user (User): The user making the request.

    Returns:
    dict: A dictionary containing artist and album data, user-specific data, and error information.
    """
    albums, artist_info, user_album_ids, user_wishlist_ids, user_blacklist_ids, user_followed_artist_ids = [], {}, [], [], [], []
    error, artist_photo_url, latest_album, artist = None, None, None, None
    collection_count, wishlist_count, blacklist_count = 0, 0, 0

    try:
        result = sp.search(q=artist_name, type='artist')
        if not result['artists']['items']:
            error = f"Artist {artist_name} not found!"
        else:
            artist_info = result['artists']['items'][0]
            artist_id = artist_info['id']
            artist_photo_url = artist_info['images'][0]['url'] if artist_info['images'] else None

            album_results = sp.artist_albums(artist_id=artist_id)
            sorted_albums = sorted(album_results['items'], key=lambda x: x['release_date'], reverse=True)
            total_albums = len(sorted_albums)

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

            artist_info.update({
                'total_albums': total_albums
            })
            if sorted_albums:
                latest_album = sorted_albums[0]

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
                    artist.save()
                    artist.refresh_from_db()

                for album in sorted_albums:
                    album_instance, created = Album.objects.get_or_create(
                        id=album['id'],
                        defaults={
                            'name': album['name'],
                            'album_type': album['album_type'],
                            'release_date': convert_to_valid_date_format(album['release_date']),
                            'image_url': album['images'][0]['url'] if album['images'] else None,
                            'artist': artist,
                        }
                    )
                        
            if user.is_authenticated:
                user_album_ids = list(UserAlbumCollection.objects.filter(user=user).values_list('album__id', flat=True))
                user_wishlist_ids = list(UserAlbumWishlist.objects.filter(user=user).values_list('album__id', flat=True))
                user_blacklist_ids = list(UserAlbumBlacklist.objects.filter(user=user).values_list('album__id', flat=True))
                user_followed_artist_ids = list(UserFollowedArtists.objects.filter(user=user).values_list('artist__id', flat=True))

                collection_count = sum(1 for album in sorted_albums if album['id'] in user_album_ids)
                wishlist_count = sum(1 for album in sorted_albums if album['id'] in user_wishlist_ids)
                blacklist_count = sum(1 for album in sorted_albums if album['id'] in user_blacklist_ids)

    except Exception as e:
        error = str(e)

    return {
        'albums': albums,
        'artist': artist,
        'error': error,
        'genres': artist_info['genres'],
        'total_albums': artist_info['total_albums'],
        'latest_album': latest_album,
        'user_album_ids': user_album_ids,
        'user_wishlist_ids': user_wishlist_ids,
        'user_blacklist_ids': user_blacklist_ids,
        'collection_count': collection_count,
        'wishlist_count': wishlist_count,
        'blacklist_count': blacklist_count,
        'user_followed_artist_ids': user_followed_artist_ids,
        'collection_and_wishlist_count': collection_count + wishlist_count,
        'progress_data': {
            'collection_count': collection_count,
            'wishlist_count': wishlist_count,
            'blacklist_count': blacklist_count,
            'collection_and_wishlist_count': collection_count + wishlist_count,
            'total_albums': artist_info['total_albums']
        }
    }