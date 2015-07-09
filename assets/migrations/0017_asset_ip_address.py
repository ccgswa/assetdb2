# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0016_auto_20150708_1615'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='ip_address',
            field=models.CharField(max_length=200, blank=True),
        ),
    ]
