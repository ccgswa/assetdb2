# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('assets', '0002_auto_20150528_0604'),
    ]

    operations = [
        migrations.AddField(
            model_name='assethistory',
            name='edited_by',
            field=models.ForeignKey(related_name='history_edited', editable=False, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='assethistory',
            name='edited_date',
            field=models.DateTimeField(null=True, editable=False),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='created_by',
            field=models.ForeignKey(related_name='history_created', editable=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
