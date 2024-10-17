from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("search/", views.artist_search, name="artist_search"),
    path('update_repo/', update_repo, name='update_repo'),
]