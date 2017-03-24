# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-06 22:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0031_auto_20170228_0002'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='affected_username',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AddField(
            model_name='log',
            name='initiating_username',
            field=models.CharField(default='prechange', max_length=150),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='log',
            name='involved_item_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
