# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 22:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0026_auto_20170226_1647'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='reason',
            field=models.TextField(default='no reason'),
            preserve_default=False,
        ),
    ]
