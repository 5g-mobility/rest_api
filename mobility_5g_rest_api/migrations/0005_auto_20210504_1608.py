# Generated by Django 3.0.5 on 2021-05-04 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobility_5g_rest_api', '0004_auto_20210503_2008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='climate',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
