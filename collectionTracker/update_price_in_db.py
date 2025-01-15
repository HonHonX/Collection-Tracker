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
from collection.models import Album
from integration.discogs_query import update_album_price
import time

application = get_wsgi_application()

# Fetch prices for all albums in the database
albums = Album.objects.all()
for album in albums:
    success = update_album_price(album.id)
    if success:
        print(f"Updated price for album {album.name} (ID: {album.id})")
    else:
        print(f"Failed to update price for album {album.name} (ID: {album.id})")
    
    # Wait for 1 second before processing the next album to avoid hitting the Discogs API rate limit
    time.sleep(1)  

# Make predictions for the future prices of the albums whose prices have been updated
updated_albums = Album.objects.filter(dailyalbumprice__isnull=False).distinct()
for album in updated_albums:
    save_album_price_predictions(None, album.id)
    print(f"Saved price predictions for album {album.name} (ID: {album.id})")

