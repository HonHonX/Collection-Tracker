from django.db.models import Count, Q
from django.db.models import Count, F, ExpressionWrapper, FloatField
from collection.models import Genre, Artist, UserAlbumCollection, UserArtistProgress, Album, User
from stats.models import Badge

def calculate_top_genres(user):
    """
    Calculate the top 5 genres based on the number of albums in the user's collection.

    Args:
        user (User): The user for whom to calculate the top genres.

    Returns:
        QuerySet: A queryset of the top 5 genres with album IDs.
    """
    top_genres = Genre.objects.annotate(
        album_count=Count(
            'artists__album__useralbumcollection',
            filter=Q(artists__album__useralbumcollection__user=user)
        )
    ).filter(album_count__gt=0).order_by('-album_count')[:5]

    for genre in top_genres:
        genre.album_ids = genre.get_album_ids()
    return top_genres

def calculate_top_artists(user):
    """
    Calculate the top 5 artists based on the number of albums in the user's collection.

    Args:
        user (User): The user for whom to calculate the top artists.

    Returns:
        QuerySet: A queryset of the top 5 artists.
    """
    return Artist.objects.annotate(
        album_count=Count(
            'album__useralbumcollection',
            filter=Q(album__useralbumcollection__user=user)
        )
    ).filter(album_count__gt=0).order_by('-album_count')[:5]

def calculate_top_quality_artists(user):
    """
    Calculate the top 5 artists based on progress percentage excluding blacklisted albums.

    Args:
        user (User): The user for whom to calculate the top quality artists.

    Returns:
        QuerySet: A queryset of the top 5 quality artists.
    """
    return UserArtistProgress.objects.filter(user=user).annotate(
        effective_total_albums=F('total_albums') - F('blacklist_count'),
        progress_percentage=ExpressionWrapper(
            (F('collection_count') + F('collection_and_wishlist_count')) * 100.0 / F('effective_total_albums'),
            output_field=FloatField()
        )
    ).order_by('-progress_percentage')[:5]

def calculate_top_friends(user):
    """
    Calculate the top 3 friends with the most similar collection.

    Args:
        user (User): The user for whom to calculate the top friends.

    Returns:
        QuerySet: A queryset of the top 3 friends with common albums and user icons.
    """
    top_friends = User.objects.filter(
        useralbumcollection__album__useralbumcollection__user=user
    ).annotate(
        common_albums=Count('useralbumcollection__album', filter=Q(useralbumcollection__album__useralbumcollection__user=user))
    ).exclude(id=user.id).order_by('-common_albums')[:3]

    for friend in top_friends:
        friend.common_album_ids = UserAlbumCollection.objects.filter(
            user=friend,
            album__useralbumcollection__user=user
        ).values_list('album__id', flat=True)
        friend.common_albums = list(Album.objects.filter(id__in=friend.common_album_ids))
        friend.icon_url = friend.profile.image.url if friend.profile.image else None
    return top_friends

def calculate_user_and_friends_ranking(user, friends_users):
    """
    Calculate the ranking of users and their friends based on collection size.

    Args:
        user (User): The user for whom to calculate the ranking.
        friends_users (QuerySet): A queryset of the user's friends.

    Returns:
        QuerySet: A queryset of the top 3 users and friends with user icons.
    """
    user_and_friends = User.objects.filter(
        Q(id=user.id) | Q(id__in=friends_users)
    ).annotate(
        collection_size=Count('useralbumcollection__album')
    ).order_by('-collection_size')[:3]

    for ranked_user in user_and_friends:
        ranked_user.icon_url = ranked_user.profile.image.url if ranked_user.profile.image else None
    return user_and_friends

def calculate_user_rank_for_artist(user, selected_artist_id):
    """
    Calculate the user's rank for the selected artist.

    Args:
        user (User): The user for whom to calculate the rank.
        selected_artist_id (int): The ID of the selected artist.

    Returns:
        tuple: A tuple containing the user's rank, the selected artist, and the number of users with more albums.
    """
    selected_artist = Artist.objects.get(id=selected_artist_id)
    user_album_count = UserAlbumCollection.objects.filter(user=user, album__artist=selected_artist).count()
    total_users = User.objects.filter(useralbumcollection__album__artist=selected_artist).distinct().count()
    users_with_more_albums = User.objects.filter(
        useralbumcollection__album__artist=selected_artist
    ).annotate(
        album_count=Count('useralbumcollection__album', filter=Q(useralbumcollection__album__artist=selected_artist))
    ).filter(album_count__gt=user_album_count).count()
    user_rank = (total_users - users_with_more_albums) / total_users * 100
    return user_rank, selected_artist, users_with_more_albums

def create_all_badges():
    """
    Create all predefined badges if they do not exist.
    """
    badges = [
        {"name": "First Friend", "description": "Awarded for adding your first friend.", "image_url": "/static/badges/first_friend.png"},
        {"name": "Five Friends", "description": "Awarded for adding five friends.", "image_url": "/static/badges/five_friends.png"},
        {"name": "First Album", "description": "Awarded for adding the first album to your collection.", "image_url": "/static/badges/first_album.png"},
    ]
    for badge_info in badges:
        Badge.objects.get_or_create(name=badge_info["name"], defaults=badge_info)

def get_or_create_badge(name, description, image_url, sub_icon_url=None):
    """
    Helper function to get or create a badge.
    
    Args:
        name (str): The name of the badge.
        description (str): The description of the badge.
        image_url (str): The URL of the badge image.
        sub_icon_url (str, optional): The URL of the sub icon image. Defaults to None.
    
    Returns:
        Badge: The badge instance.
    """
    return Badge.objects.get_or_create(name=name, defaults={
        'description': description,
        'image_url': image_url,
        'sub_icon_url': sub_icon_url
    })