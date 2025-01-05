from django.contrib import admin
from .models import Album, UserAlbumCollection, Artist, UserAlbumDescription, UserAlbumWishlist, UserAlbumBlacklist, UserArtistProgress, UserProgress, UserFollowedArtists, Genre

# Register the Genre model with the admin panel
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_artists', 'get_album_ids')
    search_fields = ('name',)

    def get_artists(self, obj):
        return ", ".join([artist.name for artist in obj.get_artists()])
    get_artists.short_description = 'Artists'

    def get_album_ids(self, obj):
        return ", ".join(obj.get_album_ids())
    get_album_ids.short_description = 'Album IDs'

# Register the Artist model with the admin panel
@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'popularity')  # Remove the many-to-many field 'genres'
    search_fields = ('name',)  # Allow searching by artist's name 
    filter_horizontal = ('genres',)  # Add genres to the admin panel

# Register the Album model with custom configuration
@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'album_type', 'release_date', 'artist')  # Include artist in the display
    search_fields = ('name', 'album_type')  # Allow searching by name and album type
    list_filter = ('album_type',)  # Optionally, filter by album type

# Register the UserAlbumCollection model with custom configuration
@admin.register(UserAlbumCollection)
class UserAlbumCollectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'added_on', 'substatus')
    list_filter = ('added_on',)  # Filter by the date the album was added

# Register the UserAlbumDescription model with custom configuration
@admin.register(UserAlbumDescription)
class UserAlbumDescriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'description')  # Display user, album, and description
    search_fields = ('user__username', 'album__name')  # Allow searching by username or album name
    list_filter = ('user',)  # Optionally, filter by user

# Register the UserAlbumWishlist model with custom configuration
@admin.register(UserAlbumWishlist)
class UserAlbumWishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'added_on', 'priority')  # Display user, album, date added, and priority
    list_filter = ('added_on',)  # Filter by the date the album was added

# Register the UserAlbumBlacklist model with custom configuration
@admin.register(UserAlbumBlacklist)
class UserAlbumBlacklistAdmin(admin.ModelAdmin):
    list_display = ('user', 'album', 'added_on')
    list_filter = ('added_on',)  # Filter by the date the album was added

# Register the UserArtistProgress model with custom configuration
@admin.register(UserArtistProgress)
class UserArtistProgressAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'artist', 'total_albums', 'collection_count', 'wishlist_count', 
        'blacklist_count', 'collection_and_wishlist_count'
    )  # Display relevant fields
    search_fields = ('user__username', 'artist__name')  # Allow searching by username and artist name
    list_filter = ('user', 'artist')  # Filter by user and artist
    readonly_fields = ('collection', 'wishlist', 'blacklist', 'collection_and_wishlist')  # Make the collection fields readonly 

# Register the UserProgress model with custom configuration
@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'total_artists', 'total_albums', 'total_collection_count', 
        'total_wishlist_count', 'total_blacklist_count', 
        'total_collection_and_wishlist_count'
    )  # Display the user's overall progress
    search_fields = ('user__username',)  # Allow searching by username
    readonly_fields = (
        'total_artists', 'total_albums', 'total_collection_count', 
        'total_wishlist_count', 'total_blacklist_count', 
        'total_collection_and_wishlist_count'
    )  # Make the aggregated fields readonly

# Register the UserFollowedArtists model with custom configuration
@admin.register(UserFollowedArtists)
class UserFollowedArtistsAdmin(admin.ModelAdmin):
    list_display = ('user', 'artist', 'followed_on')  # Display user, artist, and followed date
    search_fields = ('user__username', 'artist__name')  # Allow searching by username and artist name
    list_filter = ('artist', 'followed_on')  # Filter by the date the artist was followed