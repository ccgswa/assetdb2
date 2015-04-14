# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0004_asset_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='created_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='asset',
            name='location',
            field=models.CharField(default=b'none', max_length=4, choices=[(b'none', b'None'), (b'ccgs', b'CCGS: Main Campus'), (b'koor', b'Kooringal Campus'), (b'dmg', b'Damaged'), (b'disp', b'Disposed'), (b'lost', b'Lost or Stolen')]),
        ),
        migrations.AddField(
            model_name='asset',
            name='purchase_date',
            field=models.DateField(null=True),
        ),
    ]
