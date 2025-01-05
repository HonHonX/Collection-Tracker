from django.core.management.base import BaseCommand
from stats.models import Badge

class Command(BaseCommand):
    help = 'Create all badges in the database'

    def handle(self, *args, **kwargs):
        badges = [
            {"name": "First Album", "description": "Awarded for adding the first album to your collection.", "image_url": "/static/badges/first_album.png"},
            {"name": "First Friend", "description": "Awarded for adding your first friend.", "image_url": "/static/badges/first_friend.png"},
            {"name": "Five Friends", "description": "Awarded for adding five friends.", "image_url": "/static/badges/five_friends.png"},
        ]
        for badge_info in badges:
            Badge.objects.get_or_create(name=badge_info["name"], defaults=badge_info)
        self.stdout.write(self.style.SUCCESS('Successfully created all badges'))
