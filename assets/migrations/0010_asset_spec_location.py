# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0009_auto_20150619_1538'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='spec_location',
            field=models.CharField(max_length=200, verbose_name=b'Room/Dept', blank=True),
        ),
    ]
