# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0005_auto_20150414_0741'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='created_date',
            field=models.DateField(null=True),
        ),
    ]
