# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0011_auto_20150514_0716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='created_date',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
