from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from collection.models import UserProgress 

@login_required
def dashboard_view(request):
    user = request.user
    user_progress = UserProgress.objects.get(user=user)
    
    context = {
        'user_progress': user_progress,
    }
    return render(request, 'stats/dashboard.html', context)

