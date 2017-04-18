# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-17 23:50
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AbstractItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_name', models.CharField(max_length=100)),
                ('count', models.PositiveIntegerField(default=0)),
                ('model_number', models.CharField(max_length=100, null=True)),
                ('description', models.TextField(null=True)),
                ('is_asset', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='BackfillPDF',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf', models.FileField(upload_to='backfills/')),
            ],
        ),
        migrations.CreateModel(
            name='Cart_Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cart_reason', models.TextField()),
                ('cart_admin_comment', models.TextField(default='No Comment')),
                ('cart_status', models.CharField(choices=[('O', 'Outstanding'), ('A', 'Approved'), ('D', 'Denied'), ('P', 'In Progress'), ('L', 'Loaned'), ('B', 'Backfill')], default='O', max_length=1)),
                ('suggestion', models.CharField(choices=[('D', 'Disbursement'), ('L', 'Loan'), ('B', 'Backfill')], default='D', max_length=1)),
                ('cart_owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='CustomFieldEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('field_name', models.CharField(max_length=100, unique=True)),
                ('is_private', models.BooleanField()),
                ('value_type', models.CharField(max_length=10)),
                ('per_asset', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='EmailBody',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='EmailTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='LoanDate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('initiating_user', models.IntegerField(db_index=True)),
                ('initiating_username', models.CharField(max_length=150)),
                ('involved_item', models.IntegerField(blank=True, db_index=True, null=True)),
                ('involved_item_name', models.CharField(blank=True, max_length=100, null=True)),
                ('nature', models.TextField()),
                ('timestamp', models.DateTimeField()),
                ('related_request', models.IntegerField(blank=True, db_index=True, null=True)),
                ('affected_user', models.IntegerField(blank=True, db_index=True, null=True)),
                ('affected_username', models.CharField(blank=True, max_length=150, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.TextField()),
                ('admin_comment', models.TextField(default='No Comment')),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('status', models.CharField(choices=[('O', 'Outstanding'), ('A', 'Disbursed'), ('D', 'Denied'), ('P', 'In Progress'), ('L', 'Loaned'), ('R', 'Returned'), ('B', 'For Backfill'), ('Z', 'Hacky Log Status')], default='O', max_length=1)),
                ('suggestion', models.CharField(choices=[('D', 'Disbursement'), ('L', 'Loan'), ('B', 'Backfill')], default='D', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='SubscribedEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(max_length=100, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('abstractitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='home.AbstractItem')),
                ('asset_tag', models.PositiveIntegerField(unique=True)),
            ],
            bases=('home.abstractitem',),
        ),
        migrations.CreateModel(
            name='CustomFloatField',
            fields=[
                ('customfield_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='home.CustomField')),
                ('field_value', models.FloatField(null=True)),
            ],
            bases=('home.customfield',),
        ),
        migrations.CreateModel(
            name='CustomIntField',
            fields=[
                ('customfield_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='home.CustomField')),
                ('field_value', models.IntegerField(null=True)),
            ],
            bases=('home.customfield',),
        ),
        migrations.CreateModel(
            name='CustomLongTextField',
            fields=[
                ('customfield_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='home.CustomField')),
                ('field_value', models.TextField(null=True)),
            ],
            bases=('home.customfield',),
        ),
        migrations.CreateModel(
            name='CustomShortTextField',
            fields=[
                ('customfield_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='home.CustomField')),
                ('field_value', models.CharField(max_length=100, null=True)),
            ],
            bases=('home.customfield',),
        ),
        migrations.CreateModel(
            name='Item',
            fields=[
                ('abstractitem_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='home.AbstractItem')),
                ('name_unique_check', models.CharField(max_length=100, null=True, unique=True)),
                ('minimum_stock', models.PositiveIntegerField(default=0)),
                ('understocked', models.BooleanField(default=False)),
            ],
            bases=('home.abstractitem',),
        ),
        migrations.AddField(
            model_name='request',
            name='item_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='home.AbstractItem'),
        ),
        migrations.AddField(
            model_name='request',
            name='owner',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='request',
            name='parent_cart',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='home.Cart_Request'),
        ),
        migrations.AddField(
            model_name='customfield',
            name='field_name',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.CustomFieldEntry'),
        ),
        migrations.AddField(
            model_name='customfield',
            name='parent_item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.AbstractItem'),
        ),
        migrations.AddField(
            model_name='backfillpdf',
            name='request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.Request'),
        ),
        migrations.AddField(
            model_name='abstractitem',
            name='tags',
            field=models.ManyToManyField(to='home.Tag'),
        ),
    ]
