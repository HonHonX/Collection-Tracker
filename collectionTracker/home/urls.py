from django.urls import path
from . import views

urlpatterns = [
    # path('', views.HomeView.as_view(), name='index'),
    path('index/', views.HomeView.as_view(), name='index'),
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/remove_image/', views.remove_profile_image, name='remove_profile_image'),
]
