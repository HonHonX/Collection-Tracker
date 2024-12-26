# collection/admin.py

from django.contrib import admin
from .models import Album, UserAlbumCollection

# Register the Album model with custom configuration
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'album_type', 'release_date')
    search_fields = ('name', 'album_type')  # Allow searching by name and album type

# Register the UserAlbumCollection model with custom configuration
@admin.register(UserAlbumCollection)
class UserAlbumCollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'added_on')
    list_filter = ('added_on',)  # Filter by the date the album was added
