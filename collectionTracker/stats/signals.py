from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Count, Q
from django.contrib.auth.models import User
from django.dispatch import Signal, receiver
from friends.models import Friend, FriendList
from stats.models import Badge, UserBadge, Notification
from utils.stats_helpers import create_notification, get_or_create_badge
from collection.models import UserFollowedArtists, UserAlbumCollection, UserArtistProgress, Album, Artist
import logging
import threading

logger = logging.getLogger(__name__)

def run_in_background(func):
    """
    Decorator to run a function in a separate thread.
    
    Args:
        func (function): The function to be run in the background.
    
    Returns:
        function: The wrapped function that runs in a separate thread.
    """
    def wrapper(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return wrapper

@receiver([post_save, post_delete], sender=Friend)
@run_in_background
def award_friend_badges(sender, instance, **kwargs):
    """
    Signal receiver to award badges based on the number of friends a user has.
    
    Args:
        sender (Model): The model class that sent the signal.
        instance (Friend): The instance of the model that triggered the signal.
        **kwargs: Additional keyword arguments.
    """
    try:
        user = instance.user
        friend_count = Friend.objects.filter(user=user, status='accepted').count()

        first_friend_badge, _ = get_or_create_badge("First Friend", "Awarded for adding your first friend.", '/static/badges/first_friend.png', associated_artist=None)
        five_friends_badge, _ = get_or_create_badge("Five Friends", "Awarded for adding five friends.", '/static/badges/five_friends.png', associated_artist=None)

        if friend_count >= 1:
            user_badge, created = UserBadge.objects.get_or_create(user=user, badge=first_friend_badge)
            if created:
                create_notification(user, user_badge)
        else:
            UserBadge.objects.filter(user=user, badge=first_friend_badge).delete()

        if friend_count >= 5:
            user_badge, created = UserBadge.objects.get_or_create(user=user, badge=five_friends_badge)
            if created:
                create_notification(user, user_badge)
        else:
            UserBadge.objects.filter(user=user, badge=five_friends_badge).delete()
    except Exception as e:
        logger.error(f"Error in award_friend_badges: {e}")

@receiver([post_save, post_delete], sender=UserAlbumCollection)
@run_in_background
def award_first_album_badge(sender, instance, **kwargs):
    """
    Signal receiver to award a badge for adding the first album to the user's collection.
    
    Args:
        sender (Model): The model class that sent the signal.
        instance (UserAlbumCollection): The instance of the model that triggered the signal.
        **kwargs: Additional keyword arguments.
    """
    try:
        user = instance.user
        album_count = UserAlbumCollection.objects.filter(user=user).count()

        first_album_badge, _ = get_or_create_badge("First Album", "Awarded for adding the first album to your collection.", '/static/badges/first_album.png', associated_artist=None)

        if album_count >= 1:
            user_badge, created = UserBadge.objects.get_or_create(user=user, badge=first_album_badge)
            if created:
                create_notification(user, user_badge)
        else:
            UserBadge.objects.filter(user=user, badge=first_album_badge).delete()
    except Exception as e:
        logger.error(f"Error in award_first_album_badge: {e}")

@receiver([post_save, post_delete], sender=UserAlbumCollection)
@run_in_background
def award_collection_progress_badge(sender, instance, **kwargs):
    """
    Signal receiver to award badges based on the user's collection progress for an artist.
    
    Args:
        sender (Model): The model class that sent the signal.
        instance (UserAlbumCollection): The instance of the model that triggered the signal.
        **kwargs: Additional keyword arguments.
    """
    try:
        user = instance.user
        artist = instance.album.artist

        if artist is None:
            return

        # Calculate total albums and collection count for the artist
        total_albums = Album.objects.filter(artist=artist).count()
        collection_count = UserAlbumCollection.objects.filter(user=user, album__artist=artist).count()

        # Check if the artist is in the user's personal collection
        if collection_count == 0:
            # Ensure all badges related to the artist are deleted
            badges = Badge.objects.filter(name__icontains=artist.name)
            UserBadge.objects.filter(user=user, badge__in=badges).delete()
            return

        badges = [
            {
                'name': f"Collection Master 25%: {artist.name}",
                'description': f"Awarded for achieving 25% collection progress for {artist.name}.",
                'threshold': 0.25,
                'image_url': '/static/badges/collection_master_25.png',
            },
            {
                'name': f"Collection Master 50%: {artist.name}",
                'description': f"Awarded for achieving 50% collection progress for {artist.name}.",
                'threshold': 0.50,
                'image_url': '/static/badges/collection_master_50.png',
            },
            {
                'name': f"Collection Master 100%: {artist.name}",
                'description': f"Awarded for achieving 100% collection progress for {artist.name}.",
                'threshold': 1.00,
                'image_url': '/static/badges/collection_master_100.png',
            },
            {
                'name': f"Top Collector: {artist.name}",
                'description': f"Awarded for being the top collector for {artist.name}.",
                'image_url': '/static/badges/top_collector.png',
                'sub_icon_url': artist.photo_url,
            }
        ]

        for badge_info in badges:
            badge, _ = get_or_create_badge(badge_info['name'], badge_info['description'], badge_info['image_url'], badge_info.get('sub_icon_url'), associated_artist=artist)

            if 'threshold' in badge_info:
                progress_percentage = collection_count / total_albums

                if progress_percentage >= badge_info['threshold']:
                    user_badge, created = UserBadge.objects.get_or_create(user=user, badge=badge)
                    if created:
                        create_notification(user, user_badge)
                else:
                    UserBadge.objects.filter(user=user, badge=badge).delete()

        # Award Top Collector badge only if the artist is in the user's collection
        if collection_count > 0:
            top_collector_badge, _ = get_or_create_badge(f"Top Collector: {artist.name}", f"Awarded for being the top collector for {artist.name}.", '/static/badges/top_collector.png', artist.photo_url, associated_artist=artist)

            # Calculate ranking of users and their friends based on collection size, limited to top 3
            user_and_friends = User.objects.filter(
                Q(id=user.id) | Q(useralbumcollection__album__useralbumcollection__user=user)
            ).annotate(
                collection_size=Count('useralbumcollection__album')
            ).order_by('-collection_size')[:3]

            if user in user_and_friends:
                user_badge, created = UserBadge.objects.get_or_create(user=user, badge=top_collector_badge)
                if created:
                    create_notification(user, user_badge)
            else:
                UserBadge.objects.filter(user=user, badge=top_collector_badge).delete()
    except Exception as e:
        logger.error(f"Error in award_collection_progress_badge: {e}")

