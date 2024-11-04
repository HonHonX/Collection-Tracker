# from ChatGPT
# for register

from django.shortcuts import render, redirect  # Füge render und redirect hinzu
from django.contrib.auth import login
from django.conf import settings
from django.contrib.auth import load_backend
from .forms import RegisterForm

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Ermittlung des ersten konfigurierten Backends
            backend = load_backend(settings.AUTHENTICATION_BACKENDS[0])
            user.backend = backend.__module__ + '.' + backend.__class__.__name__
            login(request, user)  # User einloggen
            return redirect('/index')  # Nach der Registrierung auf die Startseite weiterleiten
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})  # render verwendet


