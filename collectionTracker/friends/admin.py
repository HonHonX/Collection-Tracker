from django.contrib import admin
from .models import Friend, FriendList, SharingToken

class FriendAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend_name', 'friend_email', 'status')

class FriendListAdmin(admin.ModelAdmin):
    list_display = ('user',)

class SharingTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token')

admin.site.register(Friend, FriendAdmin)
admin.site.register(FriendList, FriendListAdmin)
admin.site.register(SharingToken, SharingTokenAdmin)
