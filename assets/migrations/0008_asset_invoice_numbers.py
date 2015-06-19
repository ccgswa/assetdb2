# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0007_auto_20150611_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='invoice_numbers',
            field=models.CharField(max_length=200, verbose_name=b'Invoice Numbers', blank=True),
        ),
    ]
