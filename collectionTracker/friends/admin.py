from django.contrib import admin
from .models import Friend, FriendList, SharingToken

# Admin configuration for the Friend model
@admin.register(Friend)
class FriendAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('user', 'friend_name', 'friend_email', 'status')

# Admin configuration for the FriendList model
@admin.register(FriendList)
class FriendListAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('user',)

# Admin configuration for the SharingToken model
@admin.register(SharingToken)
class SharingTokenAdmin(admin.ModelAdmin):
    # Fields to display in the admin list view
    list_display = ('user', 'token')


