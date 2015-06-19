# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0010_asset_spec_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='location',
            field=models.CharField(default=b'none', max_length=200, choices=[(b'none', b'None'), (b'ccgs', b'Senior School'), (b'prep', b'Prep School'), (b'kooringal', b'Kooringal'), (b'damaged', b'Damaged'), (b'disposed', b'Disposed'), (b'lost', b'Lost or Stolen')]),
        ),
        migrations.AlterField(
            model_name='asset',
            name='spec_location',
            field=models.CharField(max_length=200, verbose_name=b'Room/Dept/Year', blank=True),
        ),
    ]
