# Generated by Django 4.2 on 2024-02-22 19:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0026_estateagent_agent_full_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageDimensions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('property_id', models.CharField(max_length=15, unique=True)),
                ('total_pixels', models.IntegerField()),
            ],
        ),
        migrations.AddField(
            model_name='propertydata',
            name='total_pixels',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='backend.imagedimensions'),
        ),
    ]
