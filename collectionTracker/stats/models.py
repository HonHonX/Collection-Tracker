from django.db import models
from django.contrib.auth.models import User
from collection.models import Artist, Album


class Badge(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    image_url = models.URLField()
    sub_icon_url = models.URLField(blank=True, null=True)
    associated_artist = models.ForeignKey(Artist, on_delete=models.CASCADE, blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_date']

    def __str__(self):
        return f"{self.name} - {self.associated_artist.name if self.associated_artist else 'No Artist'}"

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_badge = models.ForeignKey(UserBadge, on_delete=models.CASCADE)
    message = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True) 

    class Meta:
        ordering = ['-created_date']

    def __str__(self):
        return f"Notification for {self.user.username} - {self.user_badge.badge.name}"

class DailyAlbumPrice(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE)
    date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('album', 'date')
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.album.lowest_price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.album.name} - {self.date}: {self.price}"



