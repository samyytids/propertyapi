# Generated by Django 4.2 on 2024-02-21 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0021_image_image_height_image_image_width_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='text',
            name='description_length',
            field=models.IntegerField(null=True),
        ),
    ]