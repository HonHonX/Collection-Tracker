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

    path('', include("home.urls")),
    path('friends/', include("friends.urls")),
    path('collection/', include("collection.urls")),
    path('stats/', include("stats.urls")),
    #path('users/', include("users.urls")),
    # path('settings/', include("settings.urls")),
    path('search/', include("tracker.urls")),  # for testing
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
  
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
