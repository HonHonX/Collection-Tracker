from django.db.models.signals import post_save
from django.dispatch import receiver
from collection.models import Artist
from .discogs_query import get_more_artist_data

# @receiver(post_save, sender=Artist)
# def fetch_discogs_data(sender, instance, created, **kwargs):
#     """
#     Signal receiver to fetch Discogs data for the artist once it has been added or updated.
    
#     Args:
#         sender (Model): The model class that sent the signal.
#         instance (Artist): The instance of the model that triggered the signal.
#         created (bool): A boolean indicating whether a new record was created.
#         **kwargs: Additional keyword arguments.
#     """
#     if created:
#         # Fetch Discogs data, including a release name if provided
#         release_name = getattr(instance, 'default_release_name', None)  # Optional attribute for release
#         get_more_artist_data(instance.id, instance.name, release_name)
