# Generated by Django 5.1.1 on 2025-01-05 12:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stats', '0002_badge_sub_icon_url'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='badge',
            options={'ordering': ['created_date']},
        ),
        migrations.RenameField(
            model_name='userbadge',
            old_name='awarded_on',
            new_name='awarded_date',
        ),
        migrations.AddField(
            model_name='badge',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='badge',
            name='image_url',
            field=models.URLField(),
        ),
        migrations.AlterField(
            model_name='badge',
            name='name',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
