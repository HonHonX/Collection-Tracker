from django.db import models
from django.contrib.auth.models import User

class Album(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # Spotify ID
    name = models.CharField(max_length=200)
    album_type = models.CharField(max_length=50)  # e.g., 'album', 'single', etc.
    release_date = models.DateField()
    image_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name

class UserAlbumCollection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'album')

    def __str__(self):
        return f"{self.user.username} - {self.album.name}"
