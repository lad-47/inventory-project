# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-07 06:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_request_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='quantity',
            field=models.IntegerField(default=1),
        ),
    ]
