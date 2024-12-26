from django.urls import path

from . import views

urlpatterns = [
    path("", views.artist_search, name="artist_search"),
]