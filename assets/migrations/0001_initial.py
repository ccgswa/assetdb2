# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('name', models.CharField(max_length=30, unique=True, serialize=False, primary_key=True)),
                ('serial', models.CharField(unique=True, max_length=50)),
                ('owner', models.CharField(max_length=50)),
                ('mac', models.CharField(unique=True, max_length=50)),
                ('wmac', models.CharField(unique=True, max_length=50)),
                ('bmac', models.CharField(unique=True, max_length=50)),
            ],
        ),
    ]
