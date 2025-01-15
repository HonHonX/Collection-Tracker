from django.urls import path
from . import views
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from users.views import register, user_profile, login
from django.contrib.auth import views as auth_views
from .views import welcome_view, redirect_view, CustomPasswordResetView, CustomPasswordResetDoneView #, CustomPasswordResetCompleteView

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('accounts/', include('django.contrib.auth.urls')), # for logout, causes trouble with custom views    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', register, name='register'), # for new users
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('', views.redirect_view, name='redirect'),
    path('welcome/', views.welcome_view, name='welcome'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/remove_image/', views.remove_profile_image, name='remove_profile_image'),
    path('change-personal-color-scheme/', views.change_personal_color_scheme, name='change_personal_color_scheme'),
    path('update-email/', views.update_email, name='update_email'), 
    path('update-first-name/', views.update_first_name, name='update_first_name'), 
    path('update-last-name/', views.update_last_name, name='update_last_name'), 
    path('change-password/', views.change_password, name='change_password'),
    path('password-changed/', views.password_changed, name='password_changed'),
    path('reset-password/', CustomPasswordResetView.as_view(), name='password_reset'),    
    path('reset-password-done/', CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset-password-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/reset_password_confirm.html'), name='password_reset_confirm'),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/reset_password_complete.html'), name='password_reset_complete'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('confirm-delete-account/<str:token>/', views.confirm_delete_account, name='confirm_delete_account'),
]