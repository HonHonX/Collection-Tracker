# Generated by Django 5.1.1 on 2024-12-27 13:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('photo_url', models.URLField(blank=True, null=True)),
                ('genres', models.JSONField(default=list)),
                ('popularity', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='album',
            name='artist',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to='collection.artist'),
        ),
    ]