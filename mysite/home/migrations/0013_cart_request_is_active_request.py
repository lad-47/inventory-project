# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-17 03:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_request_parent_cart'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart_request',
            name='is_active_request',
            field=models.BooleanField(default=True),
        ),
    ]
