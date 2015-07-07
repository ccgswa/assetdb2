# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0012_auto_20150619_1604'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asset',
            old_name='spec_location',
            new_name='exact_location',
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='incident',
            field=models.CharField(default=b'general', max_length=200, choices=[(b'general', b'General Note'), (b'deploy_staff', b'Deploy to Staff'), (b'deploy_student', b'Deploy to Student'), (b'return', b'Return to ICT'), (b'lost', b'Lost or Stolen'), (b'decommission', b'Decommission'), (b'disposed', b'Disposed'), (b'other', b'Other')]),
        ),
    ]
