from django.urls import path
from . import views

urlpatterns = [
    path('', views.settings_view, name='settings'),
    path('change-color-scheme/', views.change_color_scheme, name='change_color_scheme'),
]
