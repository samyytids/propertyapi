# Generated by Django 4.2 on 2024-02-28 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0038_remove_image_image_file_image_image_binary'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagedimensions',
            name='property_id',
            field=models.CharField(max_length=15, null=True, unique=True),
        ),
    ]
