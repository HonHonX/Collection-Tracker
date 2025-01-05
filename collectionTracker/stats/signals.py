from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from stats.models import Badge, UserBadge
from collection.models import UserFollowedArtists, UserAlbumCollection, UserArtistProgress

@receiver([post_save, post_delete], sender=UserFollowedArtists)
def award_friend_badges(sender, instance, **kwargs):
    user = instance.user
    friend_count = UserFollowedArtists.objects.filter(user=user).count()

    first_friend_badge, _ = Badge.objects.get_or_create(name="First Friend", defaults={
        'description': "Awarded for adding the first friend.",
        'image_url': '/static/icons/first_friend.png'
    })
    five_friends_badge, _ = Badge.objects.get_or_create(name="Five Friends", defaults={
        'description': "Awarded for adding five friends.",
        'image_url': '/static/icons/five_friends.png'
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

@receiver([post_save, post_delete], sender=UserArtistProgress)
def award_collection_progress_badge(sender, instance, **kwargs):
    user = instance.user
    artist = instance.artist

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
        }
    ]

    for badge_info in badges:
        badge, _ = Badge.objects.get_or_create(name=badge_info['name'], defaults={
            'description': badge_info['description'],
            'image_url': badge_info['image_url'],
            'sub_icon_url': artist.photo_url  # Set the artist image as the sub icon
        })

        progress_percentage = instance.collection_count / instance.total_albums

        if progress_percentage >= badge_info['threshold']:
            UserBadge.objects.get_or_create(user=user, badge=badge)
        else:
            UserBadge.objects.filter(user=user, badge=badge).delete()
