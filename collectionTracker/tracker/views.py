from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def index(request):
    return HttpResponse("Möge der Code immer mit uns sein! Willkommen Janine, Marlon und Marius 👩‍💻✨")