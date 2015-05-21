# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0019_auto_20150515_0819'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asset',
            old_name='bmac',
            new_name='bluetooth_mac',
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='mac',
            new_name='wired_mac',
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='wmac',
            new_name='wireless_mac',
        ),
        migrations.AddField(
            model_name='asset',
            name='ed_cost',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='far_asset',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='asset',
            name='far_cost',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='warranty_period',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
