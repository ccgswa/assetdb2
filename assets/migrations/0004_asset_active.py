# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0003_auto_20150414_0649'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
