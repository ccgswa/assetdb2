# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assets', '0013_auto_20150514_0726'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='created_by',
            field=models.ForeignKey(related_name='created_by', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='assethistory',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 14, 7, 55, 28, 604084, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='assethistory',
            name='updated_by',
            field=models.ForeignKey(related_name='updated_by', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
