# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0020_auto_20150519_0917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='bluetooth_mac',
            field=models.CharField(max_length=200, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='ed_cost',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='far_cost',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='location',
            field=models.CharField(default=b'none', max_length=200, choices=[(b'none', b'None'), (b'ccgs', b'CCGS: Main Campus'), (b'kooringal', b'Kooringal Campus'), (b'damaged', b'Damaged'), (b'disposed', b'Disposed'), (b'lost', b'Lost or Stolen')]),
        ),
        migrations.AlterField(
            model_name='asset',
            name='manufacturer',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='model',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='name',
            field=models.CharField(max_length=200, unique=True, serialize=False, primary_key=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='owner',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='serial',
            field=models.CharField(unique=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='asset',
            name='warranty_period',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wired_mac',
            field=models.CharField(max_length=200, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wireless_mac',
            field=models.CharField(max_length=200, unique=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='incident',
            field=models.CharField(default=b'General', max_length=200, choices=[(b'General', b'General Note'), (b'Deploy', b'Deploy to Staff/Student'), (b'Return', b'Return to ICT'), (b'Lost', b'Lost or Stolen'), (b'Decommission', b'Decommission'), (b'Dispose', b'Dispose')]),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='recipient',
            field=models.CharField(max_length=200, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='transfer',
            field=models.CharField(default=b'Internal', max_length=200, choices=[(b'Internal', b'Internal'), (b'Incoming', b'Incoming'), (b'Outgoing', b'Outgoing')]),
        ),
    ]
