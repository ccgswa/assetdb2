# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0021_auto_20150521_0605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='bluetooth_mac',
            field=models.CharField(max_length=200, unique=True, null=True, verbose_name=b'Bluetooth MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='ed_cost',
            field=models.CharField(max_length=200, null=True, verbose_name=b'Educational Cost', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='far_asset',
            field=models.BooleanField(default=False, verbose_name=b'FAR Cost'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='serial',
            field=models.CharField(unique=True, max_length=200, verbose_name=b'Serial Number'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wired_mac',
            field=models.CharField(max_length=200, unique=True, null=True, verbose_name=b'Wired MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wireless_mac',
            field=models.CharField(max_length=200, unique=True, null=True, verbose_name=b'Wireless MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='incident',
            field=models.CharField(default=b'general', max_length=200, choices=[(b'general', b'General Note'), (b'deploy', b'Deploy to Staff/Student'), (b'return', b'Return to ICT'), (b'lost', b'Lost or Stolen'), (b'decommission', b'Decommission'), (b'dispose', b'Dispose')]),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='transfer',
            field=models.CharField(default=b'internal', max_length=200, choices=[(b'internal', b'Internal'), (b'incoming', b'Incoming'), (b'outgoing', b'Outgoing')]),
        ),
    ]
