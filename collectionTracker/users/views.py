from django.contrib.auth import login, get_backends, update_session_auth_hash
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from stats.models import Badge, UserBadge
from users.models import Profile, UserProfile

from stats import models as stats_models
from users import models as users_models
from collection import models as collection_models
from friends import models as friends_models

from .forms import RegisterForm, ProfileImageForm, CustomPasswordChangeForm, CustomPasswordResetForm
from django.db.models import Q
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.contrib.auth import logout
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_POST
import json
from django.contrib.auth.views import PasswordChangeView, PasswordResetView
from django.urls import reverse_lazy
#from collectionTracker.utils import profile_helpers

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Retrieve the first backend from AUTHENTICATION_BACKENDS
            backend = get_backends()[0]
            login(request, user, backend=backend.__module__ + '.' + backend.__class__.__name__)

            # Send a welcome email
            from django.core.mail import send_mail
            send_mail(
                subject='Welcome to Beats & Bops!',
                message=f'Hi {user.username},\n\nThank you for registering!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            ) 

            # Redirect to the homepage
            return redirect('/home')
    else:
        form = RegisterForm()

    return render(request, 'users/register.html', {'form': form, 'request': request})

def welcome_view(request):
    """
    Welcome view that displays the welcome page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered welcome page.
    """
    return render(request, 'users/welcome.html', {'settings': settings})

def redirect_view(request):
    """
    Redirect view that redirects authenticated users to the home page and unauthenticated users to the welcome page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponseRedirect: The redirection response.
    """
    if request.user.is_authenticated:
        return redirect('index')  # Update this line to use the correct view name
    else:
        return redirect('welcome')

@login_required
def user_profile(request):
    """
    View to display and update the user's profile.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered profile page.
    """
    profile, created = Profile.objects.get_or_create(user=request.user)
    badges = {badge.badge.pk: badge for badge in UserBadge.objects.filter(user=request.user).select_related('badge').order_by('awarded_date')}
    user_artists = request.user.useralbumcollection_set.values_list('album__artist', flat=True)
    all_badges = Badge.objects.filter(Q(associated_artist__isnull=True) | Q(associated_artist__in=user_artists))
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
    badge_awarded_dates = {badge.badge.pk: badge.awarded_date for badge in badges.values()}
    return render(request, 'users/profile.html', {'user': request.user, 'form': form, 'badges': badges, 'all_badges': all_badges, 'badge_awarded_dates': badge_awarded_dates})


@login_required
def remove_profile_image(request):
    """
    View to remove the user's profile image.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponseRedirect: The redirection response to the user profile page.
    """
    profile = Profile.objects.get(user=request.user)
    if profile.image:
        profile.image.delete()
        profile.save()
    return redirect('user_profile')


@login_required
def change_personal_color_scheme(request):
    """
    View to change the user's color scheme.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponseRedirect: The redirection response to the user profile page.
    """
    if request.method == 'POST':
        new_color_scheme = request.POST.get('color_scheme')
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.color_scheme = new_color_scheme
        profile.save()
    return redirect('user_profile')

@login_required
@require_POST
def update_email(request):
    old_email = request.user.email
    data = json.loads(request.body)
    new_email = data.get('email')
    if new_email:
        request.user.email = new_email
        request.user.save()

        send_mail(
            'Your email has changed',
            f'Your email has been changed from {old_email} to {new_email}. If you did not request this change, please contact us immediately and change your password.',
            settings.EMAIL_HOST_USER,
            [old_email, new_email],
            fail_silently=False,
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@require_POST
def update_first_name(request):
    data = json.loads(request.body)
    new_name = data.get('first_name')
    if new_name:
        request.user.first_name = new_name
        request.user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
@require_POST
def update_last_name(request):
    data = json.loads(request.body)
    new_name = data.get('last_name')
    if new_name:
        request.user.last_name = new_name
        request.user.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            
            # E-Mail senden
            send_mail(
                'Password changed',
                'Your password has been changed. If you did not request this change, please contact us immediately.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )
            
            return redirect('password_changed')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form})

@login_required
def password_changed(request):
    return render(request, 'users/password_changed.html')  

class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'users/password_reset.html'

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        profile = user.profile
        token = get_random_string(length=32)
        profile.deletion_token = token
        profile.save()
        
        deletion_link = request.build_absolute_uri(
            reverse('confirm_delete_account', args=[token])
        )
        
        send_mail(
            'Account Deletion Confirmation',
            f'Click the following link to confirm account deletion: {deletion_link}',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

        return JsonResponse({'message': 'Account deletion email has been sent.'})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)

@transaction.atomic
def confirm_delete_account(request, token):
    profile = get_object_or_404(users_models.Profile, deletion_token=token)
    user = profile.user

    # Löschen der abhängigen Daten aus allen Apps
    stats_models.UserBadge.objects.filter(user=user).delete()
    stats_models.Notification.objects.filter(user=user).delete()

    friends_models.Friend.objects.filter(user=user).delete()
    friends_models.FriendList.objects.filter(user=user).delete()
    friends_models.SharingToken.objects.filter(user=user).delete()  

    collection_models.UserAlbumDescription.objects.filter(user=user).delete()  
    collection_models.UserAlbumCollection.objects.filter(user=user).delete()
    collection_models.UserAlbumWishlist.objects.filter(user=user).delete()
    collection_models.UserAlbumBlacklist.objects.filter(user=user).delete() 
    collection_models.UserArtistProgress.objects.filter(user=user).delete()
    collection_models.UserProgress.objects.filter(user=user).delete()
    collection_models.UserFollowedArtists.objects.filter(user=user).delete()

    send_mail(
            'Account Deletion Successful',
            f'Your account deletion was successful. We are sorry to see you go. For new account creation, please visit our website.',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    # Löschen des UserProfile
    if hasattr(user, 'userprofile'):
        user.userprofile.delete()
    
    # Löschen des Profile
    profile.delete()
    
    # Löschen des Benutzers
    user.delete()

    logout(request)
    return render(request, 'users/account_deleted.html')



