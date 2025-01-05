from django.contrib import admin
from .models import Badge, UserBadge

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

