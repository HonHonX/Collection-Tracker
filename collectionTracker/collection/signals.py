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
            artist_albums = Album.objects.filter(artist=artist)
            total_albums = artist_albums.count()
            collection_set = set(
                UserAlbumCollection.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )
            wishlist_set = set(
                UserAlbumWishlist.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )
            progress, created = UserArtistProgress.objects.get_or_create(user=user, artist=artist)
            if created:
                logger.debug(f"Created new UserArtistProgress for user: {user.username}, artist: {artist.name}")
            else:
                logger.debug(f"Updated UserArtistProgress for user: {user.username}, artist: {artist.name}")

            progress.total_albums = total_albums
            progress.collection = list(collection_set)
            progress.wishlist = list(wishlist_set)
            progress.blacklist = list(
                UserAlbumBlacklist.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )
            progress.collection_and_wishlist = list(collection_set.intersection(wishlist_set))

            progress.collection_count = len(progress.collection)
            progress.wishlist_count = len(progress.wishlist)
            progress.blacklist_count = len(progress.blacklist)
            progress.collection_and_wishlist_count = len(progress.collection_and_wishlist)

            progress.save()

        user_progress.total_artists = Artist.objects.filter(userartistprogress__user=user).distinct().count()
        user_progress.total_collection_count = UserAlbumCollection.objects.filter(user=user).count()
        user_progress.total_wishlist_count = UserAlbumWishlist.objects.filter(user=user).count()
        user_progress.total_blacklist_count = UserAlbumBlacklist.objects.filter(user=user).count()

        collection_albums = UserAlbumCollection.objects.filter(user=user).values_list('album_id', flat=True)
        wishlist_albums = UserAlbumWishlist.objects.filter(user=user).values_list('album_id', flat=True)

        user_progress.total_collection_and_wishlist_count = len(set(collection_albums).intersection(wishlist_albums))

        user_progress.total_albums = (
            user_progress.total_collection_count + 
            user_progress.total_wishlist_count 
        )

        total_non_blacklisted_albums = user_progress.total_albums - user_progress.total_blacklist_count
        if total_non_blacklisted_albums > 0:
            user_progress.total_collection_and_wishlist_count = (
                user_progress.total_collection_and_wishlist_count / total_non_blacklisted_albums
            )
        else:
            user_progress.total_collection_and_wishlist_count = 0


        user_progress.save()

    except Exception as e:
        logger.error(f"Error updating user progress: {e}")