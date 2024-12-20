from django.shortcuts import render
from django.views import View
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.

# This is a little complex because we need to detect when we are
# running in various configurations


class HomeView(LoginRequiredMixin, View):
    def get(self, request):
        #print(request.get_host())
        #host = request.get_host()
        #islocal = host.find('localhost') >= 0 or host.find('127.0.0.1') >= 0
        #context = {
        #    'installed': settings.INSTALLED_APPS,
        #    'islocal': islocal
        #}
        #return render(request, 'home/index.html', context)
        return render(request, 'home/index.html', {'settings': settings})
    
class WelcomeView(View):
    def get(self, request):  
        return render(request, 'home/welcome.html', {'settings': settings}) 