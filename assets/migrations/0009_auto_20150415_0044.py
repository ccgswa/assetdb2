# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0008_auto_20150415_0043'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='bmac',
            field=models.CharField(max_length=50, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='mac',
            field=models.CharField(max_length=50, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wmac',
            field=models.CharField(max_length=50, unique=True, null=True, blank=True),
        ),
    ]
