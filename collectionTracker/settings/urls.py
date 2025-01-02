from django.urls import path
from .views import settings_view, change_color_scheme

urlpatterns = [
    path('', settings_view, name='settings'),
    path('change-color-scheme/', change_color_scheme, name='change_color_scheme'),
]
