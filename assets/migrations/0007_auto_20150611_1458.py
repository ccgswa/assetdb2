# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0006_auto_20150611_1455'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='bluetooth_mac',
            field=models.CharField(unique=True, max_length=200, verbose_name=b'Bluetooth MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='ed_cost',
            field=models.CharField(max_length=200, verbose_name=b'Educational Cost', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='far_cost',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='warranty_period',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wireless_mac',
            field=models.CharField(unique=True, max_length=200, verbose_name=b'Wireless MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='recipient',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
