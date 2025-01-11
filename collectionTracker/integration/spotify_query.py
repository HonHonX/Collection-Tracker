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
from integration.discogs_query import get_more_artist_data, fetch_basic_album_details

# Retrieving credentials from .env
client_id = config('SPOTIFY_CLIENT_ID')
client_secret = config('SPOTIFY_CLIENT_SECRET')

# Authentication through Spotify API
auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
sp = spotipy.Spotify(auth_manager=auth_manager)


# View for searching artist and displaying albums
def get_artist_data(artist_name, user):
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
                'id': artist_info['id'],
                'name': artist_info['name'],
                'genres': [genre for genre in artist_info['genres']],
                'popularity': artist_info['popularity'],
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
                            'release_date': album['release_date'],
                            'image_url': album['images'][0]['url'] if album['images'] else None,
                            'artist': artist,
                        }
                    )
                    if created:
                        pass
                        # print(f"Album {album_instance.name} by {album_instance.artist.name} with the id {album_instance.id} created.")

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
    } 