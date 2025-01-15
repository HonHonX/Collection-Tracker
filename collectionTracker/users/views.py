from django.contrib.auth import login, update_session_auth_hash, get_user_model
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
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.http import require_POST
import json
from django.views import View
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.views import PasswordChangeView, PasswordResetView, PasswordResetCompleteView, PasswordResetDoneView, PasswordResetConfirmView
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse_lazy
#from collectionTracker.utils import profile_helpers

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account till it is confirmed
            user.save()

            current_site = get_current_site(request)
            subject = 'Activate Your Beats & Bops Account'
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activation_link = f"http://{current_site.domain}/activate/{uid}/{token}/"
            message = f'Hi {user.username},\n\nplease click on the link below to confirm your registration: \n\n{activation_link} \n\nIf you did not make this request, you can simply ignore this email. \n\nSincerely,\nThe Beats & Bops Team'

            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False,
            )

            return redirect('account_activation_sent')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def account_activation_sent(request):
    """
    View to display the account activation sent page.

    Args:
        request: The HTTP request object.

    Returns:
        HttpResponse: The rendered account activation sent page.
    """
    return render(request, 'users/account_activation_sent.html')

User = get_user_model()

class ActivateAccount(View):
    def get(self, request, uidb64, token, *args, **kwargs):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            user.is_active = True
            user.email_verified = True
            user.save()
            login(request, user)
            send_mail(
                subject='Welcome to Beats & Bops!',
                message=f'Hi {user.username},\n\nThank you for registering! \nNow you can login to our website!',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                fail_silently=False,
            ) 
            return redirect('index')
        else:
            return render(request, 'users/account_activation_invalid.html')

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

'''
Code for password reset with custom views below
'''
class CustomPasswordResetView(PasswordResetView):
    form_class = CustomPasswordResetForm
    template_name = 'users/reset_password.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'users/reset_password_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    def form_valid(self, form):
        response = super().form_valid(form)
        self.send_confirmation_email(self.user)
        return response

    def send_confirmation_email(self, user):
        subject = 'Password successfully reset'
        message = f'Hi {user.username}! Your password has been successfully reset. If you did not make this change, please contact support immediately.'
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user.email]
        
        send_mail(subject, message, from_email, recipient_list, fail_silently=False)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'users/reset_password_complete.html'

'''
Code for account deletion below
'''
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

    # Delete dependent data from all apps
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

    # Send mail to confirm account deletion success
    send_mail(
            'Account Deletion Successful',
            f'Your account deletion was successful. We are sorry to see you go. For new account creation, please visit our website.',
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=False,
        )

    # Delete user profile 
    if hasattr(user, 'userprofile'):
        user.userprofile.delete()
    
    # Delete profile
    profile.delete()
    
    # Delete user
    user.delete()

    logout(request)
    return render(request, 'users/account_deleted.html')