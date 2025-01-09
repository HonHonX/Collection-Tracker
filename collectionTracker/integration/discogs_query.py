from decouple import config
import discogs_client
from django.shortcuts import render
from requests.exceptions import HTTPError
import json
import time
from django.db import transaction
from collection.models import Artist, Album, UserAlbumCollection, UserAlbumWishlist, UserAlbumBlacklist, UserFollowedArtists

# Retrieving credentials from .env
user_token = config('DISCOGS_TOKEN')
app = config('DISCOGS_APP_NAME')

# Create a Discogs client object with user token
d = discogs_client.Client(app, user_token=user_token)

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

    try:
        # Search for the artist
        artist_results = d.search(artist_name, type='artist')
        if not artist_results:
            raise IndexError("No artist found with the given name.")
        
        # Get the first matching artist
        artist = artist_results[0]

        # Fetch artist details including images
        artist_details = {
            'name': artist.name,
            'id': artist.id,
            'profile': getattr(artist, 'profile', 'No profile available'),
            'aliases': [alias.name for alias in getattr(artist, 'aliases', [])],
            'members': [member.name for member in getattr(artist, 'members', [])],
            'urls': getattr(artist, 'urls', []),
            'artist_image': getattr(artist, 'images', [{}])[0].get('uri', None)
        }

        # Fetch all releases (albums) and their images
        releases = artist.releases
        album_list = []
        for release in releases:
            try:
                album_image = getattr(release, 'images', [{}])[0].get('uri', None)
                release_year = getattr(release, 'year', '1900')
                release_date = f"{release_year}-01-01"
                album_list.append({
                    'title': release.title,
                    'id': release.id,
                    'year': release_date,
                    'genres': getattr(release, 'genres', []),
                    'styles': getattr(release, 'styles', []),
                    'formats': [fmt['name'] for fmt in getattr(release, 'formats', [])],
                    'labels': [label.name for label in getattr(release, 'labels', [])],
                    'tracklist': [{'position': track.position, 'title': track.title, 'duration': track.duration}
                                  for track in getattr(release, 'tracklist', [])],
                    'album_image': album_image,
                })
            except json.JSONDecodeError as e:
                error = f"JSON decoding error for release {release.id}: {e}"
                break

        # Save artist and albums to the database
        with transaction.atomic():
            artist, created = Artist.objects.get_or_create(
                id=artist_details['id'],
                defaults={
                    'name': artist_details['name'],
                    'photo_url': artist_details['artist_image'],
                    'popularity': 0,
                }
            )
            if created:
                artist.set_genres('placeholder')

            for album in album_list:
                Album.objects.get_or_create(
                    id=album['id'],
                    defaults={
                        'name': album['title'],
                        'album_type': '',
                        'release_date': album['year'],
                        'image_url': album['album_image'] if album['album_image'] else None,
                        'artist': artist,
                    }
                )

        # Get the list of user albums (user_album_ids), blacklist (user_blacklist_ids) and wishlist (user_wishlist_ids)
        if user.is_authenticated:
            user_album_ids = list(UserAlbumCollection.objects.filter(user=user).values_list('album__id', flat=True))
            user_wishlist_ids = list(UserAlbumWishlist.objects.filter(user=user).values_list('album__id', flat=True))
            user_blacklist_ids = list(UserAlbumBlacklist.objects.filter(user=user).values_list('album__id', flat=True))
            user_followed_artist_ids = list(UserFollowedArtists.objects.filter(user=user).values_list('artist__id', flat=True))

            collection_count = sum(1 for album in album_list if album['id'] in user_album_ids)
            wishlist_count = sum(1 for album in album_list if album['id'] in user_wishlist_ids)
            blacklist_count = sum(1 for album in album_list if album['id'] in user_blacklist_ids)

    except json.JSONDecodeError as e:
        error = f"JSON decoding error: {e}"
    except Exception as e:
        error = str(e)

    return {
        'albums': album_list,
        'artist_name': artist_details['name'],
        'artist_photo_url': artist_details['artist_image'],
        'error': error,
        'artist_info': artist_details,
        'latest_album': latest_album,
        'user_album_ids': user_album_ids,
        'user_wishlist_ids': user_wishlist_ids,
        'user_blacklist_ids': user_blacklist_ids,
        'collection_count': collection_count,
        'wishlist_count': wishlist_count,
        'blacklist_count': blacklist_count,
        'user_followed_artist_ids': user_followed_artist_ids,
    }
