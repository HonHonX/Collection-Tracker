from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import ProfileImageForm
from .models import Profile

# Create your views here.

# This is a little complex because we need to detect when we are
# running in various configurations


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        #print(request.get_host())
        #host = request.get_host()
        #islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0
        #context = {
        #    'installed': settings.INSTALLED_APPS,
        #    'islocal': islocal
        #}
        #return render(request, 'home/index.html', context)
        return render(request, 'home/index.html', {'settings': settings})
    
class WelcomeView(View):
    def get(self, request):  
        return render(request, 'home/welcome.html', {'settings': settings}) 
    
@login_required
def user_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES)
        if form.is_valid():
            if profile.image:
                profile.image.delete()
            image = form.cleaned_data['image']
            image.name = f"{request.user.username}_{image.name}"
            profile.image = image
            profile.save()
            return redirect('user_profile')
    else:
        form = ProfileImageForm()
    return render(request, 'home/profile.html', {'user': request.user, 'form': form})