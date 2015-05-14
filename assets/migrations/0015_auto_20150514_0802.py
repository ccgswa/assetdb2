# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0014_auto_20150514_0755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assethistory',
            name='updated_by',
            field=models.ForeignKey(related_name='added_by', to=settings.AUTH_USER_MODEL),
        ),
    ]
