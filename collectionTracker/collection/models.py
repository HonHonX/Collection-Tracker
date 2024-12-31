from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import JSONField

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

class UserAlbumWishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'album')

    def __str__(self):
        return f"{self.user.username} - Wishlist: {self.album.name}"
    
class UserAlbumBlacklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'album')

    def __str__(self):
        return f"{self.user.username} - Blacklist: {self.album.name}"

class UserArtistProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    total_albums = models.IntegerField(default=0)  # Total albums of the artist
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


# Signals to update UserArtistProgress when collection/wishlist/blacklist changes

@receiver([post_save, post_delete], sender=UserAlbumCollection)
@receiver([post_save, post_delete], sender=UserAlbumWishlist)
@receiver([post_save, post_delete], sender=UserAlbumBlacklist)
def update_user_artist_progress(sender, instance, **kwargs):
    """
    Update the UserArtistProgress model whenever the UserAlbumCollection,
    UserAlbumWishlist, or UserAlbumBlacklist model changes.
    """
    user = instance.user
    album = instance.album
    artist = album.artist

    try:
        with transaction.atomic():
            # Get or create the UserArtistProgress object for the user and artist
            progress, created = UserArtistProgress.objects.get_or_create(user=user, artist=artist)

            # Query all albums related to this artist
            artist_albums = Album.objects.filter(artist=artist)

            # Calculate the total albums
            progress.total_albums = artist_albums.count()

            # Albums in the user's collection (convert to list)
            progress.collection = list(
                UserAlbumCollection.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )

            # Albums in the user's wishlist (convert to list)
            progress.wishlist = list(
                UserAlbumWishlist.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )

            # Albums in the user's blacklist (convert to list)
            progress.blacklist = list(
                UserAlbumBlacklist.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )

            # Convert lists to sets before performing intersection
            collection_set = set(progress.collection)
            wishlist_set = set(progress.wishlist)

            # Albums in both collection and wishlist (convert to list)
            progress.collection_and_wishlist = list(collection_set.intersection(wishlist_set))

            # Update the counts
            progress.collection_and_wishlist_count = len(progress.collection_and_wishlist)
            progress.collection_count = len(collection_set - wishlist_set)  # Only in collection
            progress.wishlist_count = len(wishlist_set - collection_set)  # Only in wishlist
            progress.blacklist_count = len(progress.blacklist)

            # Save the progress
            progress.save()

    except Exception as e:
        # Optionally log the error or handle it in some way
        print(f"Error updating user artist progress: {e}")

