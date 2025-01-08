from django.contrib import admin
from .models import Badge, UserBadge, Notification

# Register the Badge model with the admin panel
@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_url', 'sub_icon_url')
    search_fields = ('name',)

# Register the UserBadge model with the admin panel
@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_date')
    search_fields = ('user__username', 'badge__name')
    list_filter = ('awarded_date',)

# Register the Notification model with the admin panel
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_badge', 'message', 'created_date')
    search_fields = ('user__username', 'user_badge__badge__name', 'message')
    list_filter = ('created_date',)

