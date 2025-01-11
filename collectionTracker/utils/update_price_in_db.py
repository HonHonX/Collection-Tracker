from integration.discogs_query import update_album_price
from collection.models import Album
import time

albums = Album.objects.all()
for album in albums:
    success = update_album_price(album.id)
    if success:
        print(f"Updated price for album {album.name} (ID: {album.id})")
    else:
        print(f"Failed to update price for album {album.name} (ID: {album.id})")
    time.sleep(1)  # Wait for 1 second before processing the next album
