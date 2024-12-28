from django.contrib import admin
from .models import Album, UserAlbumCollection, Artist, UserAlbumDescription

# Register the Artist model with the admin panel
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Display artist's id and name
    search_fields = ('name',)  # Allow searching by artist's name

# Register the Album model with custom configuration
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'album_type', 'release_date', 'artist')  # Include artist in the display
    search_fields = ('name', 'album_type')  # Allow searching by name and album type
    list_filter = ('album_type',)  # Optionally, filter by album type

# Register the UserAlbumCollection model with custom configuration
@admin.register(UserAlbumCollection)
class UserAlbumCollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'added_on')
    list_filter = ('added_on',)  # Filter by the date the album was added

# Register the UserAlbumDescription model with custom configuration
@admin.register(UserAlbumDescription)
class UserAlbumDescriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'description')  # Display user, album, and description
    search_fields = ('user__username', 'album__name')  # Allow searching by username or album name
    list_filter = ('user',)  # Optionally, filter by user
