# models.py
from django.contrib.auth.models import User
from django.db import models

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