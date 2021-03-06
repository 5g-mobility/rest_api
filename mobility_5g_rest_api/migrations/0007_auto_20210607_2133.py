# Generated by Django 3.0.5 on 2021-06-07 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mobility_5g_rest_api', '0006_auto_20210603_2237'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='climate',
            index=models.Index(fields=['location', 'condition'], name='mobility_5g_locatio_a4e3b3_idx'),
        ),
        migrations.AddIndex(
            model_name='climate',
            index=models.Index(fields=['location', '-timestamp'], name='mobility_5g_locatio_eef2e8_idx'),
        ),
        migrations.AddIndex(
            model_name='climate',
            index=models.Index(fields=['-timestamp'], name='mobility_5g_timesta_a85491_idx'),
        ),
        migrations.AddIndex(
            model_name='dailyinflow',
            index=models.Index(fields=['location', '-date'], name='mobility_5g_locatio_96366c_idx'),
        ),
        migrations.AddIndex(
            model_name='dailyinflow',
            index=models.Index(fields=['-date'], name='mobility_5g_date_7bccb2_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['location', 'event_type', 'event_class', '-timestamp'], name='mobility_5g_locatio_46c4d7_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['location', 'event_type', '-timestamp'], name='mobility_5g_locatio_1e84f6_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['location', 'event_class', '-timestamp'], name='mobility_5g_locatio_2ea010_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['-timestamp', 'event_type', '-velocity'], name='mobility_5g_timesta_b8e085_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['-timestamp'], name='mobility_5g_timesta_d3304c_idx'),
        ),
        migrations.AddIndex(
            model_name='event',
            index=models.Index(fields=['-velocity'], name='mobility_5g_velocit_2128cb_idx'),
        ),
        migrations.AddIndex(
            model_name='radarevent',
            index=models.Index(fields=['-timestamp', 'radar_id'], name='mobility_5g_timesta_193a46_idx'),
        ),
    ]
