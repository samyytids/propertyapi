# Generated by Django 4.2 on 2024-01-31 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0015_alter_epc_epc_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ownership',
            name='rent_frequency',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
