# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0014_auto_20150708_1532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='serial',
            field=models.CharField(db_index=True, unique=True, max_length=200, verbose_name=b'Serial Number', blank=True),
        ),
    ]
