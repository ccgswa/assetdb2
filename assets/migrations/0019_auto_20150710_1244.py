# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0018_auto_20150709_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='purchase_date',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='created_date',
            field=models.DateTimeField(),
        ),
    ]
