# Generated by Django 4.2.7 on 2023-11-22 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0023_alter_estateagentaccreditation_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='property',
            name='url',
            field=models.URLField(),
        ),
    ]
