# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0004_auto_20150528_0807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assethistory',
            name='asset',
            field=models.ForeignKey(editable=False, to='assets.Asset'),
        ),
    ]
