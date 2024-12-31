# Generated by Django 5.1.1 on 2024-12-31 13:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('collection', '0014_alter_useralbumdescription_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useralbumdescription',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='useralbumwishlist',
            name='priority',
            field=models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (0, 'Unspecified')], default=0),
        ),
    ]
