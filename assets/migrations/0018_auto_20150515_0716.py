# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0017_auto_20150515_0652'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='asset',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='created_date',
        ),
        migrations.RemoveField(
            model_name='assethistory',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='assethistory',
            name='created_date',
        ),
    ]
