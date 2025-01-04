from django.db import models, transaction
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import JSONField

# models.py
class Artist(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default=0)  # Spotify ID
    name = models.CharField(max_length=100)
    photo_url = models.URLField(blank=True, null=True)
    genres = models.JSONField(default=list)
    popularity = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.name} - ID: {self.id} " 

class Album(models.Model):
    id = models.CharField(max_length=50, primary_key=True)  # Spotify ID
    name = models.CharField(max_length=200)
    album_type = models.CharField(max_length=50)
    release_date = models.DateField()
    image_url = models.URLField(blank=True, null=True)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name 
    
class UserAlbumDescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)  # Allow null values

    def save(self, *args, **kwargs):
        # Strip whitespace before saving
        self.description = self.description.strip() if self.description else None
        
        super().save(*args, **kwargs)

class UserAlbumCollection(models.Model):
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    followed_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'artist')

    def __str__(self):
        return f"{self.user.username} follows {self.artist.name}"

# Signals to update UserArtistProgress/UserProgress when collection/wishlist/blacklist changes
@receiver([post_save, post_delete], sender=UserAlbumCollection)
@receiver([post_save, post_delete], sender=UserAlbumWishlist)
@receiver([post_save, post_delete], sender=UserAlbumBlacklist)
def update_user_progress(sender, instance, **kwargs):
    """
    Update the UserArtistProgress and UserProgress models whenever the UserAlbumCollection,
    UserAlbumWishlist, or UserAlbumBlacklist model changes.
    """
    user = instance.user
    album = instance.album

    # Check if the album still has an associated artist
    if not album.artist_id:
        return

    try:
        artist = album.artist
    except Artist.DoesNotExist:
        return

    try:
        with transaction.atomic():
            # Get or create the UserArtistProgress object for the user and artist
            progress, created = UserArtistProgress.objects.get_or_create(user=user, artist=artist)

            # Query all albums related to this artist
            artist_albums = Album.objects.filter(artist=artist)

            # Calculate the total albums
            progress.total_albums = artist_albums.count()

            # Albums in the user's collection
            collection_set = set(
                UserAlbumCollection.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )

            # Albums in the user's wishlist
            wishlist_set = set(
                UserAlbumWishlist.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )

            # Update progress fields
            progress.collection = list(collection_set)
            progress.wishlist = list(wishlist_set)
            progress.blacklist = list(
                UserAlbumBlacklist.objects.filter(user=user, album__artist=artist)
                .values_list('album__id', flat=True)
            )
            progress.collection_and_wishlist = list(collection_set.intersection(wishlist_set))

            # Update the counts
            progress.collection_and_wishlist_count = len(progress.collection_and_wishlist)
            progress.collection_count_total = len(progress.collection)
            progress.collection_count = progress.collection_count_total - progress.collection_and_wishlist_count
            progress.wishlist_count_total = len(progress.wishlist)
            progress.wishlist_count = progress.wishlist_count_total - progress.collection_and_wishlist_count
            progress.blacklist_count = len(progress.blacklist)

            progress.save()

            # Update UserProgress for the user
            user_progress, created = UserProgress.objects.get_or_create(user=user)

            user_progress.total_artists = Artist.objects.filter(userartistprogress__user=user).distinct().count()
            user_progress.total_collection_count = UserAlbumCollection.objects.filter(user=user).count()
            user_progress.total_wishlist_count = UserAlbumWishlist.objects.filter(user=user).count()
            user_progress.total_blacklist_count = UserAlbumBlacklist.objects.filter(user=user).count()

            # Fetch albums in both collection and wishlist for the user
            collection_albums = UserAlbumCollection.objects.filter(user=user).values_list('album_id', flat=True)
            wishlist_albums = UserAlbumWishlist.objects.filter(user=user).values_list('album_id', flat=True)

            # Calculate the intersection of albums in both collection and wishlist
            user_progress.total_collection_and_wishlist_count = len(set(collection_albums).intersection(wishlist_albums))

            # Calculate the total number of albums the user has in their collection, wishlist, and blacklist combined
            user_progress.total_albums = (
                user_progress.total_collection_count + 
                user_progress.total_wishlist_count 
            )

            user_progress.save()

    except Exception as e:
        # Handle error and log it
        print(f"Error updating user progress: {e}")

