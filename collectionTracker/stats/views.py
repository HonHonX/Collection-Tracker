from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from collection.models import UserProgress, Genre, UserAlbumCollection, Artist
from django.db.models import Count, Q

@login_required
def dashboard_view(request):
    user = request.user
    try:
        user_progress = UserProgress.objects.get(user=user)
    except UserProgress.DoesNotExist:
        user_progress = UserProgress.objects.create(user=user)

    # Calculate top 5 genres based on the number of albums in the user's collection
    top_genres = Genre.objects.annotate(
        album_count=Count(
            'artists__album__useralbumcollection',
            filter=Q(artists__album__useralbumcollection__user=user)
        )
    ).filter(album_count__gt=0).order_by('-album_count')[:5]

    # Add album IDs for each genre
    for genre in top_genres:
        genre.album_ids = genre.get_album_ids()

    # Calculate top 10 artists based on the number of albums in the user's collection
    top_artists = Artist.objects.annotate(
        album_count=Count(
            'album__useralbumcollection',
            filter=Q(album__useralbumcollection__user=user)
        )
    ).filter(album_count__gt=0).order_by('-album_count')[:5]

    context = {
        'user_progress': user_progress,
        'top_genres': top_genres,
        'top_artists': top_artists,
    }
    return render(request, 'stats/dashboard.html', context)


