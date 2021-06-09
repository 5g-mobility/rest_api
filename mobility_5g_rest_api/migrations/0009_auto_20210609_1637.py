# Generated by Django 3.0.5 on 2021-06-09 16:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobility_5g_rest_api', '0008_auto_20210607_2144'),
    ]

    operations = [
        migrations.AlterField(
            model_name='event',
            name='velocity',
            field=models.IntegerField(blank=True, validators=[django.core.validators.MaxValueValidator(400), django.core.validators.MinValueValidator(-400)]),
        ),
        migrations.AlterField(
            model_name='radarevent',
            name='radar_id',
            field=models.CharField(choices=[('1', 'Duna'), ('7', 'Ria Ativa'), ('5', 'Ponte Barra')], max_length=1),
        ),
    ]