from django.db import models
from django.contrib.auth.models import User
import uuid

class Friend(models.Model):
    """
    Model representing a friend relationship.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    friend_name = models.CharField(max_length=100, blank=True)
    friend_email = models.EmailField()
    status = models.CharField(max_length=10, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('guest', 'Guest')], default='pending')

    def __str__(self):
        """
        String representation of the Friend model.
        """
        return f"{self.user.username} - {self.friend_email} ({self.status})"

class FriendList(models.Model):
    """
    Model representing a user's list of friends.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='friend_list')
    friends = models.ManyToManyField(Friend, blank=True)

    def __str__(self):
        """
        String representation of the FriendList model.
        """
        return f"{self.user.username}'s friends"

def generate_unique_token():
        """
        Generate a unique token using UUID.
        """
        return str(uuid.uuid4())

class SharingToken(models.Model):
    """
    Model representing a sharing token for a user.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_token')
    token = models.CharField(default=generate_unique_token, max_length=36, unique=True)

    def __str__(self):
        """
        String representation of the SharingToken model.
        """
        return f"{self.user.username} - {self.token}"
    