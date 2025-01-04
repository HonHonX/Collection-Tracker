from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return self.user.username

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    color_scheme = models.CharField(max_length=100, choices=[
        ('spring', 'Spring Theme'),
        ('summer', 'Summer Theme'),
        ('autumn', 'Autumn Theme'),
        ('winter', 'Winter Theme'),
    ], default='winter')

    def __str__(self):
        return self.user.username
