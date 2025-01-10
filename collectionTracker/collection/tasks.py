import threading
from .models import Artist
from integration.discogs_query import save_basic_album_details
from integration.discogs_query import get_more_artist_data
import logging

logger = logging.getLogger(__name__)

def save_album_details_in_background(artist_id):
    # logger.info(f"Running background task for artist ID: {artist_id}")
    # save_basic_album_details(artist_id)
    pass

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
    thread = threading.Thread(target=update_artist_details_in_background, args=(artist_id,))
    thread.start()

def start_background_task(artist_id):
    # thread = threading.Thread(target=save_album_details_in_background, args=(artist_id,))
    # thread.start()
    pass