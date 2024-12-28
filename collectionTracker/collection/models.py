from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator

# models.py

class Artist(models.Model):
    name = models.CharField(max_length=100)
    photo_url = models.URLField(blank=True, null=True)
    genres = models.JSONField(default=list)  # Stores genres as a list of strings
    popularity = models.IntegerField(default=0)
    
    def __str__(self):
        return self.name

class Album(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # Spotify ID
    name = models.CharField(max_length=200)
    album_type = models.CharField(max_length=50)
    release_date = models.DateField()
    image_url = models.URLField(blank=True, null=True)
    artist = models.ForeignKey(Artist, on_delete=models.SET_NULL, null=True)

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

class UserAlbumDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    description = models.TextField(
        blank=True,
        validators=[MinLengthValidator(1)]  # Optional: enforce minimum length
    )

    def save(self, *args, **kwargs):
        # Strip whitespace before saving
        self.description = self.description.strip()
        super().save(*args, **kwargs)
