# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0012_auto_20150514_0725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
