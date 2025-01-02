from django.contrib import admin
from .models import Friend, FriendList

class FriendAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email')

class FriendListAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(Friend, FriendAdmin)
admin.site.register(FriendList, FriendListAdmin)
