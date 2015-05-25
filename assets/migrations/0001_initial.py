# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=200, db_index=True)),
                ('manufacturer', models.CharField(max_length=200, null=True, blank=True)),
                ('model', models.CharField(max_length=200, null=True, blank=True)),
                ('serial', models.CharField(unique=True, max_length=200, verbose_name=b'Serial Number')),
                ('location', models.CharField(default=b'none', max_length=200, choices=[(b'none', b'None'), (b'ccgs', b'CCGS: Main Campus'), (b'kooringal', b'Kooringal Campus'), (b'damaged', b'Damaged'), (b'disposed', b'Disposed'), (b'lost', b'Lost or Stolen')])),
                ('owner', models.CharField(max_length=200, null=True, blank=True)),
                ('purchase_date', models.DateField(null=True, blank=True)),
                ('wired_mac', models.CharField(max_length=200, unique=True, null=True, verbose_name=b'Wired MAC', blank=True)),
                ('wireless_mac', models.CharField(max_length=200, unique=True, null=True, verbose_name=b'Wireless MAC', blank=True)),
                ('bluetooth_mac', models.CharField(max_length=200, unique=True, null=True, verbose_name=b'Bluetooth MAC', blank=True)),
                ('far_asset', models.BooleanField(default=False, verbose_name=b'FAR Cost')),
                ('far_cost', models.CharField(max_length=200, null=True, blank=True)),
                ('ed_cost', models.CharField(max_length=200, null=True, verbose_name=b'Educational Cost', blank=True)),
                ('warranty_period', models.CharField(max_length=200, null=True, blank=True)),
                ('active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssetHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('incident', models.CharField(default=b'general', max_length=200, choices=[(b'general', b'General Note'), (b'deploy', b'Deploy to Staff/Student'), (b'return', b'Return to ICT'), (b'lost', b'Lost or Stolen'), (b'decommission', b'Decommission'), (b'dispose', b'Dispose')])),
                ('recipient', models.CharField(max_length=200, null=True, blank=True)),
                ('transfer', models.CharField(default=b'internal', max_length=200, choices=[(b'internal', b'Internal'), (b'incoming', b'Incoming'), (b'outgoing', b'Outgoing')])),
                ('notes', models.TextField(null=True, blank=True)),
                ('asset', models.ForeignKey(to='assets.Asset')),
            ],
        ),
    ]
