# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0015_auto_20150708_1601'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='location',
            field=models.CharField(default=b'none', max_length=200, choices=[(b'none', b'None'), (b'ccgs', b'CCGS Main Campus'), (b'kooringal', b'Kooringal Campus'), (b'damaged', b'Damaged'), (b'disposed', b'Disposed'), (b'lost', b'Lost or Stolen')]),
        ),
    ]
