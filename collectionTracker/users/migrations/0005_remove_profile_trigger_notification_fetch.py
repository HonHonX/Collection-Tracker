# Generated by Django 5.1.1 on 2025-01-18 13:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_profile_trigger_notification_fetch'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='trigger_notification_fetch',
        ),
    ]
