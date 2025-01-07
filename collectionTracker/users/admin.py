from django.contrib import admin
from .models import Profile, UserProfile

admin.site.register(Profile)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'color_scheme',)
