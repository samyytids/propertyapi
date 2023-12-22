# Generated by Django 4.2 on 2023-12-22 12:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_alter_lettinginfo_let_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='affiliation',
            name='affiliation_name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='businesstype',
            name='property_id',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='businesstype',
            name='sector',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='businesstype',
            name='use_class',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='epc',
            name='ei_caption',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='epc',
            name='epc_caption',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='epc',
            name='property_id',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='estateagent',
            name='agent_description',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='estateagent',
            name='agent_name',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='estateagent',
            name='agent_type',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='estateagent',
            name='agent_url_type',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='estateagent',
            name='branch_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='floorplan',
            name='floorplan_caption',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='image',
            name='image_caption',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='keyfeature',
            name='feature',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='layout',
            name='property_id',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='lettinginfo',
            name='property_id',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='address',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='location',
            name='property_id',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='ownership',
            name='property_id',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='ownership',
            name='rent_frequency',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='price',
            name='original_price',
            field=models.BooleanField(),
        ),
        migrations.AlterField(
            model_name='property',
            name='property_id',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='propertydata',
            name='furnished',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='propertydata',
            name='letting_type',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='propertydata',
            name='pre_owned',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='propertydata',
            name='property_id',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='propertydata',
            name='property_sub_type',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='propertydata',
            name='property_type',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_description',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='room',
            name='room_name',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='station',
            name='station_name',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='stationdistance',
            name='station_distance',
            field=models.DecimalField(decimal_places=10, max_digits=20),
        ),
        migrations.AlterField(
            model_name='tax',
            name='property_id',
            field=models.CharField(max_length=15, unique=True),
        ),
        migrations.AlterField(
            model_name='text',
            name='property_id',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
