from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import JSONField, CharField
from django.contrib.postgres.fields import ArrayField
import json

class Genre(models.Model):
    """Model representing a music genre."""
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    def get_artists(self):
        """Return all artists associated with this genre."""
        return self.artists.all()

    def album_count(self): 
        """Return the count of albums associated with this genre.""" 
        return Album.objects.filter(artist__genres=self).count()

    def get_album_ids(self):
        """Return a list of album IDs associated with this genre."""
        return Album.objects.filter(artist__genres=self).values_list('id', flat=True)

class Artist(models.Model): 
    """Model representing a music artist."""
    id = models.CharField(max_length=50, primary_key=True, default=0) 
    name = models.CharField(max_length=100)
    photo_url = models.URLField(blank=True, null=True)
    genres = models.ManyToManyField(Genre, related_name='artists')
    popularity = models.IntegerField(default=0)

    # Attributes provided by discogs
    discogs_id = models.IntegerField(blank=True, null=True)
    profile = CharField(max_length=1000, default='N/A', blank=True, null=True)
    aliases = JSONField(default=list, blank=True, null=True)  # Store as JSON field
    members = JSONField(default=list, blank=True, null=True)  # Store as JSON field
    urls = JSONField(default=list, blank=True, null=True)  # Store as JSON field
    
    def __str__(self): 
        return f"{self.name} - ID: {self.id}, Discogs: {self.discogs_id}, Profile: {self.profile} " 

    def set_genres(self, genre_names):
        """Set genres for the artist based on a list of genre names."""
        genres = [Genre.objects.get_or_create(name=name)[0] for name in genre_names]
        self.genres.set(genres)

class Album(models.Model):
    """Model representing a music album."""
    id = models.CharField(max_length=50, primary_key=True) 
    name = models.CharField(max_length=200)
    album_type = models.CharField(max_length=50)
    release_date = models.DateField() 
    image_url = models.URLField(blank=True, null=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True)

    # Attributes provided by Discogs
    discogs_id = models.IntegerField(blank=True, null=True)
    genres = JSONField(default=list, blank=True, null=True)  # Store as JSON field
    styles = JSONField(default=list, blank=True, null=True)  # Store as JSON field
    tracklist = JSONField(default=list, blank=True, null=True)  # Store as JSON field
    labels = JSONField(default=list, blank=True, null=True)  # Store as JSON field
    lowest_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name 

class UserAlbumDescription(models.Model):
    """Model representing a user's description of an album."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)  # Allow null values

    def save(self, *args, **kwargs):
        """Override save method to strip whitespace before saving."""
        self.description = self.description.strip() if self.description else None
        super().save(*args, **kwargs)

class UserAlbumCollection(models.Model):
    """Model representing a user's album collection."""
    SUBSTATUS = [
        ('delivered', 'Delivered'),
        ('preordered', 'Preordered'),
        ('ordered', 'Ordered'),
        ('unspecified', 'Unspecified'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    substatus = models.CharField(
        max_length=25,
        choices=SUBSTATUS, 
        default='unspecified',
    )

    class Meta:
        unique_together = ('user', 'album')

    def __str__(self):
        return f"{self.user.username} - {self.album.name} (Substatus: {self.get_substatus_display()})"

class UserAlbumWishlist(models.Model):
    """Model representing a user's album wishlist."""
    PRIORITY_CHOICES = [
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (0, 'Unspecified'),
    ]
     
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES, 
        default=0,
    )

    class Meta:
        unique_together = ('user', 'album')

    def __str__(self):
        return f"{self.user.username} - Wishlist: {self.album.name} (Priority: {self.get_priority_display()})"
    
class UserAlbumBlacklist(models.Model):
    """Model representing a user's album blacklist."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'album')

    def __str__(self):
        return f"{self.user.username} - Blacklist: {self.album.name}"

class UserArtistProgress(models.Model):
    """Model representing a user's progress with a specific artist."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    total_albums = models.IntegerField(default=0)  # Total albums of the selected artist
    collection = JSONField(default=list)  # Albums only in the user's collection
    wishlist = JSONField(default=list)  # Albums only in the user's wishlist
    blacklist = JSONField(default=list)  # Albums in the user's blacklist
    collection_and_wishlist = JSONField(default=list)  # Albums in both collection and wishlist
    collection_count = models.IntegerField(default=0)  # Albums only in the user's collection
    wishlist_count = models.IntegerField(default=0)  # Albums only in the user's wishlist
    blacklist_count = models.IntegerField(default=0)  # Albums in the user's blacklist
    collection_and_wishlist_count = models.IntegerField(default=0)  # Albums in both collection and wishlist

    class Meta:
        unique_together = ('user', 'artist')

    def __str__(self):
        return f"{self.user.username} - {self.artist.name} Progress"

class UserProgress(models.Model):
    """Model representing a user's overall progress."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_artists = models.IntegerField(default=0)  # Number of artists the user has interacted with
    total_albums = models.IntegerField(default=0)  # Total number of albums the user has in collection, wishlist, blacklist
    total_collection_count = models.IntegerField(default=0)  # Total albums in collection
    total_wishlist_count = models.IntegerField(default=0)  # Total albums in wishlist
    total_blacklist_count = models.IntegerField(default=0)  # Total albums in blacklist
    total_collection_and_wishlist_count = models.IntegerField(default=0)  # Total albums in both collection and wishlist
 
    def __str__(self):
        return f"{self.user.username}'s Progress" 
    
class UserFollowedArtists(models.Model):
    """Model representing artists followed by a user."""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    followed_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'artist')

    def __str__(self):
        return f"{self.user.username} follows {self.artist.name}"


