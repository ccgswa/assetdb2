# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0003_auto_20150528_0636'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assethistory',
            name='edited_date',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='incident',
            field=models.CharField(default=b'general', max_length=200, choices=[(b'general', b'General Note'), (b'deploy', b'Deploy to Staff/Student'), (b'return', b'Return to ICT'), (b'lost', b'Lost or Stolen'), (b'decommission', b'Decommission'), (b'dispose', b'Dispose'), (b'other', b'Other')]),
        ),
    ]
