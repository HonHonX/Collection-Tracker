"""collectionTracker URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from . import views
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views    # for github login
from django.views.generic import TemplateView    # for github login
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # for login / logout
    path('register/', views.register, name='register'), # for new users
    re_path(r'^oauth/', include('social_django.urls', namespace='social')), # for github login

    path('', include("home.urls")),
    path('friends/', include("friends.urls")),
    path('collection/', include("collection.urls")),
    path('stats/', include("stats.urls")),
    #path('users/', include("users.urls")),
    path('settings/', include("settings.urls")),
 
    path("search/", include("tracker.urls")),  # for testing
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# https://github.com/csev/dj4e-samples/blob/main/dj4e-samples/urls.py
# for login with github
try:
    from . import github_settings
    social_login = 'registration/login.html'
    urlpatterns.insert(0,
                       path('accounts/login/', auth_views.LoginView.as_view(template_name=social_login))
                       )
except:
    print('Using registration/login.html as the login template')