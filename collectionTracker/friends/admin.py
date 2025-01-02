from django.contrib import admin
from .models import Friend, FriendList

class FriendAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend_name', 'friend_email', 'status')

class FriendListAdmin(admin.ModelAdmin):
    list_display = ('user',)

admin.site.register(Friend, FriendAdmin)
admin.site.register(FriendList, FriendListAdmin)
