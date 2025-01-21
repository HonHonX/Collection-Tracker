from django.contrib import admin
from .models import Badge, UserBadge, Notification, DailyAlbumPrice, AlbumPricePrediction


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'image_url', 'sub_icon_url')
    search_fields = ('name',)

@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'awarded_date')
    search_fields = ('user__username', 'badge__name')
    list_filter = ('awarded_date',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_badge', 'message', 'created_date')
    search_fields = ('user__username', 'user_badge__badge__name', 'message')
    list_filter = ('created_date',)

@admin.register(DailyAlbumPrice)
class DailyAlbumPriceAdmin(admin.ModelAdmin):
    list_display = ('album', 'date', 'price')
    search_fields = ('album__name', 'date')
    list_filter = ('date',)

@admin.register(AlbumPricePrediction)
class AlbumPricePredictionAdmin(admin.ModelAdmin):
    list_display = ('album', 'date', 'predicted_price')
    search_fields = ('album__name', 'date')


