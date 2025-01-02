from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile

def settings_view(request):
    return render(request, 'settings/settings.html')

@login_required
def change_color_scheme(request):
    if request.method == 'POST':
        new_color_scheme = request.POST.get('color_scheme')
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.color_scheme = new_color_scheme
        profile.save()
    return redirect('settings')
