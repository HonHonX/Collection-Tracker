# Generated by Django 5.1.1 on 2025-01-01 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0016_useralbumcollection_substatus'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artist',
            name='id',
            field=models.CharField(max_length=50, primary_key=True, serialize=False),
        ),
    ]