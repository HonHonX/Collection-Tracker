from django.db import models
from django.contrib.auth.models import User

class Badge(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    image_url = models.URLField()
    sub_icon_url = models.URLField(blank=True, null=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_date']

    def __str__(self):
        return self.name

class UserBadge(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    awarded_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'badge')

    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
