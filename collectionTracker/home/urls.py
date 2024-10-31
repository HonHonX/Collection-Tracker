from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view()),
    path('welcome/', views.WelcomeView.as_view()),
]
