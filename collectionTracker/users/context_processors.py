# from https://github.com/csev/dj4e-samples/blob/main/home/context_processors.py
# for login with github

from django.conf import settings as django_settings

def settings(request):
    return {
        'settings': django_settings,
    }