from django.shortcuts import render
from django.views import View


# Create your views here.

class album_overview(View):
    def get(self, request):  
        return render(request, 'collection/album_overview.html') 
    
class album_detail(View):
    def get(self, request):  
        return render(request, 'collection/album_detail.html')    