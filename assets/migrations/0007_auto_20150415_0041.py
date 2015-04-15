# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0006_auto_20150414_0743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='manufacturer',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='model',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='owner',
            field=models.CharField(max_length=50, null=True, blank=True),
        ),
    ]
