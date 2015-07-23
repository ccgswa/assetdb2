# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0019_auto_20150710_1244'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asset',
            name='bluetooth_mac',
            field=models.CharField(db_index=True, max_length=200, verbose_name=b'Bluetooth MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='exact_location',
            field=models.CharField(db_index=True, max_length=200, verbose_name=b'Year/Dept/Room', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='location',
            field=models.CharField(default=b'none', max_length=200, choices=[(b'none', b'--------------------'), (b'ccgs', b'CCGS Main Campus'), (b'kooringal', b'Kooringal Campus'), (b'damaged', b'Damaged'), (b'disposed', b'Disposed'), (b'lost', b'Lost or Stolen')]),
        ),
        migrations.AlterField(
            model_name='asset',
            name='model',
            field=models.CharField(db_index=True, max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='owner',
            field=models.CharField(db_index=True, max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='purchase_date',
            field=models.DateField(help_text=b'Please use the following format: <em>YYYY-MM-DD</em>.', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wired_mac',
            field=models.CharField(db_index=True, max_length=200, verbose_name=b'Wired MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='wireless_mac',
            field=models.CharField(db_index=True, max_length=200, verbose_name=b'Wireless MAC', blank=True),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='created_date',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='assethistory',
            name='incident',
            field=models.CharField(default=b'general', max_length=200, choices=[(b'general', b'General Note'), (b'deploy_staff', b'Deploy to Staff'), (b'deploy_student', b'Deploy to Student'), (b'return', b'Return to ICT'), (b'lost', b'Lost or Stolen'), (b'decommission', b'Decommission'), (b'disposed', b'Disposed')]),
        ),
    ]
