from django.urls import path
from . import views

urlpatterns = [
    path("album_overview/", views.album_overview.as_view()),
    path("album_detail/", views.album_detail.as_view()),
]