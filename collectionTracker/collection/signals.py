import logging
from django.db import transaction
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import UserAlbumCollection, UserAlbumWishlist, UserAlbumBlacklist, UserArtistProgress, UserProgress, Artist, Album

# Set up logging
logger = logging.getLogger(__name__)

@receiver([post_save, post_delete], sender=UserAlbumCollection)
@receiver([post_save, post_delete], sender=UserAlbumWishlist)
@receiver([post_save, post_delete], sender=UserAlbumBlacklist)
def update_user_progress(sender, instance, **kwargs):
    """
    Update the UserArtistProgress and UserProgress models whenever the UserAlbumCollection,
    UserAlbumWishlist, or UserAlbumBlacklist model changes.
    """
    user = instance.user
    album = instance.album

    logger.debug(f"Signal received for user: {user.username}, album: {album.name}")

    # Check if the album still has an associated artist
    if not album.artist_id:
        logger.debug("Album has no associated artist.")
        return

    try:
        artist = album.artist
    except Artist.DoesNotExist:
        logger.debug("Artist does not exist.")
        return
    
    logger.debug(f"Artist: {artist.name}")

    user_progress, created = UserProgress.objects.get_or_create(user=user)
    if created:
        logger.debug(f"Created new UserProgress for user: {user.username}")
    else:
        logger.debug(f"Updated UserProgress for user: {user.username}")

    try:
        with transaction.atomic():
            logger.debug("Updating user progress...")

            # Query all albums related to this artist
            artist_albums = Album.objects.filter(artist=artist)
            logger.debug(f"Albums for artist {artist.name}: {artist_albums}")

            # Calculate the total albums
            total_albums = artist_albums.count()
            logger.debug(f"Total albums for artist {artist.name}: {total_albums}")

            # Albums in the user's collection
            collection_set = set(
                UserAlbumCollection.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )
            logger.debug(f"Collection set for user {user.username}: {collection_set}")

            # Albums in the user's wishlist
            wishlist_set = set(
                UserAlbumWishlist.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )
            logger.debug(f"Wishlist set for user {user.username}: {wishlist_set}")

            logger.debug(f"User:{user}: Artist: {artist}")
            # Get or create the UserArtistProgress object for the user and artist
            progress, created = UserArtistProgress.objects.get_or_create(user=user, artist=artist)
            if created:
                logger.debug(f"Created new UserArtistProgress for user: {user.username}, artist: {artist.name}")
            else:
                logger.debug(f"Updated UserArtistProgress for user: {user.username}, artist: {artist.name}")

            # Update progress fields
            progress.total_albums = total_albums
            progress.collection = list(collection_set)
            progress.wishlist = list(wishlist_set)
            progress.blacklist = list(
                UserAlbumBlacklist.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )
            progress.collection_and_wishlist = list(collection_set.intersection(wishlist_set))

            # Update the counts
            progress.collection_count = len(progress.collection)
            progress.wishlist_count = len(progress.wishlist)
            progress.blacklist_count = len(progress.blacklist)
            progress.collection_and_wishlist_count = len(progress.collection_and_wishlist)

            logger.debug(f"Progress for user {user.username}, artist {artist.name}: {progress}")

            progress.save()

        # Update UserProgress for the user
        user_progress.total_artists = Artist.objects.filter(userartistprogress__user=user).distinct().count()
        user_progress.total_collection_count = UserAlbumCollection.objects.filter(user=user).count()
        user_progress.total_wishlist_count = UserAlbumWishlist.objects.filter(user=user).count()
        user_progress.total_blacklist_count = UserAlbumBlacklist.objects.filter(user=user).count()

        # Fetch albums in both collection and wishlist for the user
        collection_albums = UserAlbumCollection.objects.filter(user=user).values_list('album_id', flat=True)
        wishlist_albums = UserAlbumWishlist.objects.filter(user=user).values_list('album_id', flat=True)

        # Calculate the intersection of albums in both collection and wishlist
        user_progress.total_collection_and_wishlist_count = len(set(collection_albums).intersection(wishlist_albums))

        # Calculate the total number of albums the user has in their collection, wishlist, and blacklist combined
        user_progress.total_albums = (
            user_progress.total_collection_count + 
            user_progress.total_wishlist_count 
        )

        # Ensure no division by zero
        total_non_blacklisted_albums = user_progress.total_albums - user_progress.total_blacklist_count
        if total_non_blacklisted_albums > 0:
            user_progress.total_collection_and_wishlist_count = (
                user_progress.total_collection_and_wishlist_count / total_non_blacklisted_albums
            )
        else:
            user_progress.total_collection_and_wishlist_count = 0

        logger.debug(f"UserProgress for user {user.username}: {user_progress}")

        user_progress.save()

    except Exception as e:
        # Handle error and log it
        logger.error(f"Error updating user progress: {e}")