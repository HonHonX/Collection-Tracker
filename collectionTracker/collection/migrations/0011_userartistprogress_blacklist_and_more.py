# Generated by Django 5.1.1 on 2024-12-31 00:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0010_userartistprogress'),
    ]

    operations = [
        migrations.AddField(
            model_name='userartistprogress',
            name='blacklist',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='userartistprogress',
            name='collection',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='userartistprogress',
            name='collection_and_wishlist',
            field=models.JSONField(default=list),
        ),
        migrations.AddField(
            model_name='userartistprogress',
            name='wishlist',
            field=models.JSONField(default=list),
        ),
    ]
