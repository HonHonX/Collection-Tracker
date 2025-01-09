from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('friends/', include("friends.urls")),
    path('', include("collection.urls")),
    path('stats/', include("stats.urls")),
    path('', include("users.urls")),
    path('accounts/', include('django.contrib.auth.urls')), 
] + static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
