# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0002_auto_20150414_0529'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='bmac',
            field=models.CharField(max_length=50, unique=True, null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='mac',
            field=models.CharField(max_length=50, unique=True, null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='owner',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wmac',
            field=models.CharField(max_length=50, unique=True, null=True),
        ),
    ]
