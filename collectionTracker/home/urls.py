from django.urls import path
from . import views

urlpatterns = [
    path('', views.WelcomeView.as_view()),
    path('index/', views.HomeView.as_view()),
]
