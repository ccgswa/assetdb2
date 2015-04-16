# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0009_auto_20150415_0044'),
    ]

    operations = [
        migrations.CreateModel(
            name='AssetHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('incident', models.CharField(default=b'gen', max_length=4, choices=[(b'gen', b'General Note'), (b'depl', b'Deploy to Staff/Student'), (b'ict', b'Return to ICT'), (b'lost', b'Lost or Stolen'), (b'dec', b'Decommission'), (b'disp', b'Disposed')])),
                ('recipient', models.CharField(max_length=50, null=True, blank=True)),
                ('transfer', models.CharField(default=b'int', max_length=4, choices=[(b'int', b'Internal'), (b'inc', b'Incoming'), (b'out', b'Outgoing')])),
                ('notes', models.TextField(null=True, blank=True)),
                ('asset', models.ForeignKey(to='assets.Asset')),
            ],
        ),
    ]
