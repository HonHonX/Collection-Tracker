from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from users.views import register, user_profile
from .views import welcome_view, redirect_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')), # for login / logout
    path('register/', register, name='register'), # for new users
    path('', views.redirect_view, name='redirect'),
    path('welcome/', views.welcome_view, name='welcome'),
    path('profile/', user_profile, name='user_profile'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/remove_image/', views.remove_profile_image, name='remove_profile_image'),
    path('change-personal-color-scheme/', views.change_personal_color_scheme, name='change_personal_color_scheme'),
]
  