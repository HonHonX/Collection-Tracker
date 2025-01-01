from django.contrib.auth import login, get_backends
from django.shortcuts import render, redirect
from django.conf import settings
from .forms import RegisterForm  # Ensure you import your custom RegisterForm

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
            return redirect('/index')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})

