# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-21 04:09
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0017_log'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='affected_user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='affected_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
