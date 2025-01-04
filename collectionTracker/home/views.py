from django.shortcuts import render, redirect
from django.views import View
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import ProfileImageForm
from .models import Profile, UserProfile
from collection.models import UserFollowedArtists, Album, UserAlbumCollection, UserAlbumWishlist, UserAlbumBlacklist

# Create your views here.
class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        followed_artists = []
        if request.user.is_authenticated:
            followed_artists = UserFollowedArtists.objects.filter(user=request.user).select_related('artist').order_by('followed_on')
            for followed_artist in followed_artists:
                followed_artist.albums = Album.objects.filter(artist=followed_artist.artist)

        #print(request.get_host())
        #host = request.get_host()
        #islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0
        #context = {
        #    'installed': settings.INSTALLED_APPS,
        #    'islocal': islocal
        #}
        #return render(request, 'home/index.html', context)   

        user_album_ids = UserAlbumCollection.objects.filter(user=request.user).values_list('album__id', flat=True)
        user_blacklist_ids = UserAlbumBlacklist.objects.filter(user=request.user).values_list('album__id', flat=True)
        user_wishlist_ids = UserAlbumWishlist.objects.filter(user=request.user).values_list('album__id', flat=True)

        return render(request, 'home/index.html', {
            'settings': settings,
            'followed_artists': followed_artists,
            'user_album_ids': user_album_ids, 
            'user_blacklist_ids': user_blacklist_ids,
            'user_wishlist_ids': user_wishlist_ids,
        })
    
    
class WelcomeView(View):
    def get(self, request):  
        return render(request, 'home/welcome.html', {'settings': settings}) 
    
class RedirectView(View):
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('index')
        else:
            return redirect('welcome')

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

@login_required
def remove_profile_image(request):
    profile = Profile.objects.get(user=request.user)
    if profile.image:
        profile.image.delete()
        profile.save()
    return redirect('user_profile')

@login_required
def change_color_scheme(request):
    if request.method == 'POST':
        new_color_scheme = request.POST.get('color_scheme')
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.color_scheme = new_color_scheme
        profile.save()
    return redirect('user_profile')