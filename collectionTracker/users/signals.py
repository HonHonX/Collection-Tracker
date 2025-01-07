from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile, UserProfile

@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    """
    Signal to create Profile and UserProfile instances when a new User is created.
    """
    if created:
        Profile.objects.create(user=instance)
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profiles(sender, instance, **kwargs):
    """
    Signal to save the Profile and UserProfile instances when the User is saved.
    """
    instance.profile.save()
    instance.userprofile.save()
