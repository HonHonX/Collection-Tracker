# Generated by Django 5.1.1 on 2025-01-04 01:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0018_alter_artist_id_userfollowedartists'),
    ]

    operations = [
        migrations.AlterField(
            model_name='album',
            name='artist',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='collection.artist'),
        ),
    ]
