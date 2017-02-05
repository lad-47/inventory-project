# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-04 08:47
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0005_remove_request_testfield'),
    ]

    operations = [
        migrations.AddField(
            model_name='request',
            name='item_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='home.Item'),
        ),
        migrations.AddField(
            model_name='request',
            name='user_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]