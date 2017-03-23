# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-28 04:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0027_request_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfloatfield',
            name='field_value',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customintfield',
            name='field_value',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customlongtextfield',
            name='field_value',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='customshorttextfield',
            name='field_value',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
