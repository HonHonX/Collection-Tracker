# Generated by Django 5.1.1 on 2025-01-05 01:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0019_alter_album_artist'),
    ]

    operations = [
        migrations.CreateModel(
            name='Genre',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='artist',
            name='genres',
        ),
        migrations.AddField(
            model_name='artist',
            name='genres',
            field=models.ManyToManyField(related_name='artists', to='collection.genre'),
        ),
    ]
