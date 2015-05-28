# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assets', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assethistory',
            name='created_by',
            field=models.ForeignKey(default=1, editable=False, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='assethistory',
            name='created_date',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 28, 6, 4, 5, 539083, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='asset',
            name='far_asset',
            field=models.BooleanField(default=False, verbose_name=b'FAR Asset'),
        ),
    ]
