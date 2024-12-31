# Generated by Django 5.1.1 on 2024-12-31 00:15

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0009_useralbumblacklist'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='UserArtistProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total_albums', models.IntegerField(default=0)),
                ('collection_count', models.IntegerField(default=0)),
                ('wishlist_count', models.IntegerField(default=0)),
                ('blacklist_count', models.IntegerField(default=0)),
                ('collection_and_wishlist_count', models.IntegerField(default=0)),
                ('artist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collection.artist')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'artist')},
            },
        ),
    ]
