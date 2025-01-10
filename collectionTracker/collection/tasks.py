import threading
from .models import Artist
from integration.discogs_query import save_basic_album_details
import logging

logger = logging.getLogger(__name__)

def save_album_details_in_background(artist_id):
    logger.info(f"Running background task for artist ID: {artist_id}")
    save_basic_album_details(artist_id)

def start_background_task(artist_id):
    thread = threading.Thread(target=save_album_details_in_background, args=(artist_id,))
    thread.start()