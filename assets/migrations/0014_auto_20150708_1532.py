# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0013_auto_20150707_1702'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='location',
            field=models.CharField(default=b'none', max_length=200, choices=[(b'none', b'None'), (b'senior', b'Senior School'), (b'prep', b'Prep School'), (b'kooringal', b'Kooringal'), (b'damaged', b'Damaged'), (b'disposed', b'Disposed'), (b'lost', b'Lost or Stolen')]),
        ),
    ]
