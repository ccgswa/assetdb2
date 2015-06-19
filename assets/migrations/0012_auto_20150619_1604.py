# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0011_auto_20150619_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='spec_location',
            field=models.CharField(max_length=200, verbose_name=b'Year/Dept/Room', blank=True),
        ),
    ]
