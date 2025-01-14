import os
import sys

# Add the root directory of the project to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'collectionTracker.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from collection.models import Album
from integration.discogs_query import update_album_price
import time

albums = Album.objects.all()
for album in albums:
    success = update_album_price(album.id)
    if success:
        print(f"Updated price for album {album.name} (ID: {album.id})")
    else:
        print(f"Failed to update price for album {album.name} (ID: {album.id})")
    time.sleep(1)  # Wait for 1 second before processing the next album
