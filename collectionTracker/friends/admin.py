from django.contrib import admin
from .models import Friend, FriendList, SharingToken

@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    list_display = ('user', 'friend_name', 'friend_email', 'status')

@admin.register(FriendList)
class FriendListAdmin(admin.ModelAdmin):
    list_display = ('user',)

@admin.register(SharingToken)
class SharingTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'token')


