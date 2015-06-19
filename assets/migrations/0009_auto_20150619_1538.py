# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('assets', '0008_asset_invoice_numbers'),
    ]

    operations = [
        migrations.RenameField(
            model_name='asset',
            old_name='invoice_numbers',
            new_name='invoices',
        ),
    ]
