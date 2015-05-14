# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0010_assethistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 14, 7, 16, 59, 693901, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
    ]
