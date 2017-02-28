# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-28 04:10
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0028_auto_20170227_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customfloatfield',
            name='field_value',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='customintfield',
            name='field_value',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='customlongtextfield',
            name='field_value',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='customshorttextfield',
            name='field_value',
            field=models.CharField(max_length=100, null=True),
        ),
    ]