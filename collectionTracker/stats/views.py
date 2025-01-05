from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from collection.models import UserProgress, Genre
from django.db.models import Count

@login_required
def dashboard_view(request):
    user = request.user
    try:
        user_progress = UserProgress.objects.get(user=user)
    except UserProgress.DoesNotExist:
        user_progress = UserProgress.objects.create(user=user)

    # Calculate top 5 genres based on the number of albums in the user's collection
    top_genres = Genre.objects.annotate(
        album_count=Count('artists__album')
    ).order_by('-album_count')[:5]

    context = {
        'user_progress': user_progress,
        'top_genres': top_genres,
    }
    return render(request, 'stats/dashboard.html', context)


 