# Generated by Django 3.0.5 on 2021-04-21 01:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mobility_5g_rest_api', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dailyinflow',
            name='temperature',
        ),
    ]
