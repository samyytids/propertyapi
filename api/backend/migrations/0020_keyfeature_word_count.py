# Generated by Django 4.2 on 2024-02-08 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0019_alter_floorplan_property_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyfeature',
            name='word_count',
            field=models.IntegerField(default=12),
            preserve_default=False,
        ),
    ]