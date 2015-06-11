# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0005_auto_20150529_0341'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='manufacturer',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='model',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='owner',
            field=models.CharField(max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='purchase_date',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='serial',
            field=models.CharField(unique=True, max_length=200, verbose_name=b'Serial Number', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wired_mac',
            field=models.CharField(unique=True, max_length=200, verbose_name=b'Wired MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='incident',
            field=models.CharField(default=b'general', max_length=200, choices=[(b'general', b'General Note'), (b'deploy_staff', b'Deploy to Staff'), (b'deploy_student', b'Deploy to Student'), (b'return', b'Return to ICT'), (b'lost', b'Lost or Stolen'), (b'decommission', b'Decommission'), (b'dispose', b'Dispose'), (b'other', b'Other')]),
        ),
    ]
