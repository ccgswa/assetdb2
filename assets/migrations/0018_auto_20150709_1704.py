# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0017_asset_ip_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='bluetooth_mac',
            field=models.CharField(max_length=200, verbose_name=b'Bluetooth MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='serial',
            field=models.CharField(db_index=True, max_length=200, verbose_name=b'Serial Number', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wired_mac',
            field=models.CharField(max_length=200, verbose_name=b'Wired MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wireless_mac',
            field=models.CharField(max_length=200, verbose_name=b'Wireless MAC', blank=True),
        ),
    ]
