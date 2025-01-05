from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from friends.models import Friend, FriendList
from stats.models import Badge, UserBadge
from collection.models import UserFollowedArtists, UserAlbumCollection, UserArtistProgress, Album, Artist
from django.db.models import Count, Q
from django.contrib.auth.models import User

def create_all_badges():
    badges = [
        {"name": "First Friend", "description": "Awarded for adding your first friend.", "image_url": "/static/badges/first_friend.png"},
        {"name": "Five Friends", "description": "Awarded for adding five friends.", "image_url": "/static/badges/five_friends.png"},
        {"name": "First Album", "description": "Awarded for adding the first album to your collection.", "image_url": "/static/badges/first_album.png"},
    ]
    for badge_info in badges:
        Badge.objects.get_or_create(name=badge_info["name"], defaults=badge_info)

@receiver([post_save, post_delete], sender=Friend)
def award_friend_badges(sender, instance, **kwargs):
    user = instance.user
    friend_count = Friend.objects.filter(user=user, status='accepted').count()

    first_friend_badge, _ = Badge.objects.get_or_create(name="First Friend", defaults={
        'description': "Awarded for adding your first friend.",
        'image_url': '/static/badges/first_friend.png'
    })
    five_friends_badge, _ = Badge.objects.get_or_create(name="Five Friends", defaults={
        'description': "Awarded for adding five friends.",
        'image_url': '/static/badges/five_friends.png'
    })

    if friend_count >= 1:
        UserBadge.objects.get_or_create(user=user, badge=first_friend_badge)
    else:
        UserBadge.objects.filter(user=user, badge=first_friend_badge).delete()

    if friend_count >= 5:
        UserBadge.objects.get_or_create(user=user, badge=five_friends_badge)
    else:
        UserBadge.objects.filter(user=user, badge=five_friends_badge).delete()

@receiver([post_save, post_delete], sender=UserAlbumCollection)
def award_first_album_badge(sender, instance, **kwargs):
    user = instance.user
    album_count = UserAlbumCollection.objects.filter(user=user).count()

    first_album_badge, _ = Badge.objects.get_or_create(name="First Album", defaults={
        'description': "Awarded for adding the first album to your collection.",
        'image_url': '/static/badges/first_album.png'
    })

    if album_count >= 1:
        UserBadge.objects.get_or_create(user=user, badge=first_album_badge)
    else:
        UserBadge.objects.filter(user=user, badge=first_album_badge).delete()

@receiver([post_save, post_delete], sender=UserAlbumCollection)
def award_collection_progress_badge(sender, instance, **kwargs):
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
            'image_url': '/static/badges/collection_master_25.png'
        },
        {
            'name': f"Collection Master 50%: {artist.name}",
            'description': f"Awarded for achieving 50% collection progress for {artist.name}.",
            'threshold': 0.50,
            'image_url': '/static/badges/collection_master_50.png'
        },
        {
            'name': f"Collection Master 100%: {artist.name}",
            'description': f"Awarded for achieving 100% collection progress for {artist.name}.",
            'threshold': 1.00,
            'image_url': '/static/badges/collection_master_100.png'
        },
        {
            'name': f"Top Collector: {artist.name}",
            'description': f"Awarded for being the top collector for {artist.name}.",
            'image_url': '/static/badges/top_collector.png',
            'sub_icon_url': artist.photo_url
        }
    ]

    for badge_info in badges:
        badge, _ = Badge.objects.get_or_create(name=badge_info['name'], defaults={
            'description': badge_info['description'],
            'image_url': badge_info['image_url'],
            'sub_icon_url': badge_info.get('sub_icon_url')
        })

        if 'threshold' in badge_info:
            progress_percentage = collection_count / total_albums

            if progress_percentage >= badge_info['threshold']:
                UserBadge.objects.get_or_create(user=user, badge=badge)
            else:
                UserBadge.objects.filter(user=user, badge=badge).delete()

    # Award Top Collector badge
    top_collector_badge, _ = Badge.objects.get_or_create(name=f"Top Collector: {artist.name}", defaults={
        'description': f"Awarded for being the top collector for {artist.name}.",
        'image_url': '/static/badges/top_collector.png',
        'sub_icon_url': artist.photo_url
    })

    # Calculate ranking of users and their friends based on collection size, limited to top 3
    user_and_friends = User.objects.filter(
        Q(id=user.id) | Q(useralbumcollection__album__useralbumcollection__user=user)
    ).annotate(
        collection_size=Count('useralbumcollection__album')
    ).order_by('-collection_size')[:3]

    if user in user_and_friends:
        UserBadge.objects.get_or_create(user=user, badge=top_collector_badge)
    else:
        UserBadge.objects.filter(user=user, badge=top_collector_badge).delete()