from django.urls import path
from . import views

urlpatterns = [
    path('', views.WelcomeView.as_view(), name='welcome'),
    path('index/', views.HomeView.as_view(), name='index'),
]
