# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-03 07:01
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20170127_1515'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='item_id',
        ),
        migrations.RemoveField(
            model_name='request',
            name='status',
        ),
        migrations.RemoveField(
            model_name='request',
            name='user_id',
        ),
    ]