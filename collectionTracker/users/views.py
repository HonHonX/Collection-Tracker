from django.contrib.auth import login, get_backends
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from stats.models import Badge, UserBadge
from users.models import Profile, UserProfile
from .forms import RegisterForm, ProfileImageForm

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
    all_badges = Badge.objects.all()
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



