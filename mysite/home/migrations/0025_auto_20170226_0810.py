# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-26 13:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0024_auto_20170224_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfieldentry',
            name='field_name',
            field=models.CharField(max_length=100, unique=True),
        ),
    ]
