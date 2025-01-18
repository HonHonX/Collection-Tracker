from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    """
    Profile model that extends the User model with additional fields:
    - a profile image field
    - a deletion token field
    - an email verified field 
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    deletion_token = models.CharField(max_length=32, blank=True, null=True)
    email_verified = models.BooleanField(default=False)

    @staticmethod
    def get_or_create_profile(user):
        profile, created = Profile.objects.get_or_create(user=user)
        return profile

    def __str__(self):
        """
        String representation of the Profile model.
        """
        return self.user.username

User.profile = property(Profile.get_or_create_profile)

class UserProfile(models.Model):
    """
    UserProfile model that extends the User model with a color theme field.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    color_scheme = models.CharField(max_length=100, choices=[
        ('spring', 'Spring Theme'),
        ('summer', 'Summer Theme'),
        ('autumn', 'Autumn Theme'),
        ('winter', 'Winter Theme'),
    ], default='winter') 

    def __str__(self):
        """
        String representation of the UserProfile model.
        """
        return self.user.username
