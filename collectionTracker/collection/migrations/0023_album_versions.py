# Generated by Django 5.1.1 on 2025-01-10 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0022_album_current_price_album_discogs_id_album_formats_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='album',
            name='versions',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
