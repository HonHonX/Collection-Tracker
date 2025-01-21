import threading
from .models import Artist, Album
from integration.discogs_query import get_more_artist_data, fetch_basic_album_details
import logging

logger = logging.getLogger(__name__)

def update_artist_details_in_background(artist_id):
    try:
        artist = Artist.objects.get(id=artist_id)
        if not artist.discogs_id:
            artist_data = get_more_artist_data(artist.name)
            artist.discogs_id = artist_data.get('discogs_id')
            artist.profile = artist_data.get('profile')
            artist.aliases = artist_data.get('aliases')
            artist.members = artist_data.get('members')
            artist.urls = artist_data.get('urls')
            artist.save()
            logger.info(f"Updated artist {artist.name} with new Discogs data.")
        else:
            logger.info(f"Artist {artist.name} already has a Discogs ID.") 
    except Artist.DoesNotExist:
        logger.error(f"Artist with ID {artist_id} does not exist.")

def start_background_artist_update(artist_id):
    thread_artist = threading.Thread(target=update_artist_details_in_background, args=(artist_id,))
    thread_artist.start()

def update_album_details(album_id):
    try:
        album = Album.objects.get(id=album_id)
        album_data = fetch_basic_album_details(album.id)
        album.discogs_id = album_data.get('discogs_id')
        album.genres = album_data.get('genres')
        album.styles = album_data.get('styles')
        album.labels = album_data.get('labels')
        album.tracklist = album_data.get('tracklist')
        album.lowest_price = album_data.get('lowest_price')
        album.save()
        logger.info(f"Updated album {album.name} with new Discogs data.")
    except Album.DoesNotExist:
        logger.error(f"Album with ID {album_id} does not exist.")

def start_background_album_update(album_id):
    thread_album = threading.Thread(target=update_album_details, args=(album_id,))
    thread_album.start()