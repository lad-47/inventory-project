# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-16 21:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_merge_20170416_1743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='request',
            name='status',
            field=models.CharField(choices=[('O', 'Outstanding'), ('A', 'Disbursed'), ('D', 'Denied'), ('P', 'In Progress'), ('L', 'Loaned'), ('R', 'Returned'), ('B', 'For Backfill'), ('Z', 'Hacky Log Status')], default='O', max_length=1),
        ),
    ]
