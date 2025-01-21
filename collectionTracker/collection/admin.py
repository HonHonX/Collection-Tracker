from django.contrib import admin
from .models import Album, UserAlbumCollection, Artist, UserAlbumDescription, UserAlbumWishlist, UserAlbumBlacklist, UserArtistProgress, UserProgress, UserFollowedArtists, Genre, RecommendedArtist

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """
    Admin interface for the Genre model.
    """
    list_display = ('name', 'get_artists', 'get_album_ids')
    search_fields = ('name',)

    def get_artists(self, obj):
        """
        Return a comma-separated list of artists for the genre.
        
        Args:
            obj (Genre): The genre object.
        
        Returns:
            str: A comma-separated list of artist names.
        """
        return ", ".join([artist.name for artist in obj.get_artists()])
    get_artists.short_description = 'Artists'

    def get_album_ids(self, obj):
        """
        Return a comma-separated list of album IDs for the genre.
        
        Args:
            obj (Genre): The genre object.
        
        Returns:
            str: A comma-separated list of album IDs.
        """
        return ", ".join(obj.get_album_ids())
    get_album_ids.short_description = 'Album IDs'

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    """
    Admin interface for the Artist model.
    """
    list_display = ('name', 'id', 'photo_url', 'popularity', 'discogs_id', 'profile')
    search_fields = ('name', 'id', 'discogs_id')
    filter_horizontal = ('genres',)

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    """
    Admin interface for the Album model.
    """
    list_display = ('id', 'name', 'album_type', 'release_date', 'artist', 'discogs_id', 'lowest_price')
    search_fields = ('name', 'album_type', 'discogs_id')
    list_filter = ('album_type', 'release_date')
    readonly_fields = ('id',)
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'artist', 'release_date', 'album_type', 'image_url')
        }),
        ('Discogs Data', {
            'fields': ('discogs_id', 'genres', 'styles', 'tracklist', 'labels', 'lowest_price')
        }),
    )

@admin.register(UserAlbumCollection)
class UserAlbumCollectionAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserAlbumCollection model.
    """
    list_display = ('user', 'album', 'added_on', 'substatus')
    list_filter = ('added_on',)

@admin.register(UserAlbumDescription)
class UserAlbumDescriptionAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserAlbumDescription model.
    """
    list_display = ('user', 'album', 'description')
    search_fields = ('user__username', 'album__name')
    list_filter = ('user',)

@admin.register(UserAlbumWishlist)
class UserAlbumWishlistAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserAlbumWishlist model.
    """
    list_display = ('user', 'album', 'added_on', 'priority')
    list_filter = ('added_on',)

@admin.register(UserAlbumBlacklist)
class UserAlbumBlacklistAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserAlbumBlacklist model.
    """
    list_display = ('user', 'album', 'added_on')
    list_filter = ('added_on',)

@admin.register(UserArtistProgress)
class UserArtistProgressAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserArtistProgress model.
    """
    list_display = (
        'user', 'artist', 'total_albums', 'collection_count', 'wishlist_count', 
        'blacklist_count', 'collection_and_wishlist_count'
    )
    search_fields = ('user__username', 'artist__name')
    list_filter = ('user', 'artist')
    readonly_fields = ('collection', 'wishlist', 'blacklist', 'collection_and_wishlist')

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserProgress model.
    """
    list_display = (
        'user', 'total_artists', 'total_albums', 'total_collection_count', 
        'total_wishlist_count', 'total_blacklist_count', 
        'total_collection_and_wishlist_count'
    )
    search_fields = ('user__username',)
    readonly_fields = (
        'total_artists', 'total_albums', 'total_collection_count', 
        'total_wishlist_count', 'total_blacklist_count', 
        'total_collection_and_wishlist_count'
    )

@admin.register(UserFollowedArtists)
class UserFollowedArtistsAdmin(admin.ModelAdmin):
    """
    Admin interface for the UserFollowedArtists model.
    """
    list_display = ('user', 'artist', 'followed_on')
    search_fields = ('user__username', 'artist__name')
    list_filter = ('artist', 'followed_on')

@admin.register(RecommendedArtist)
class RecommendedArtistAdmin(admin.ModelAdmin):
    """
    Admin interface for the RecommendedArtist model.
    """
    list_display = ('user', 'artist', 'created_at')
    search_fields = ('user__username', 'artist__name')
    list_filter = ('created_at',)


