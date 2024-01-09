# Generated by Django 4.2 on 2023-12-21 22:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='text',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='text',
            name='disclaimer',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='text',
            name='new_homes_brochure_disclaimer',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='text',
            name='page_title',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='text',
            name='share_description',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='text',
            name='share_text',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='text',
            name='short_description',
            field=models.TextField(),
        ),
    ]