# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-04 10:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0006_auto_20170630_0838'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='switch',
            options={'permissions': (('switch_view', 'can view Switch state'),)},
        ),
        migrations.AlterField(
            model_name='led',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
    ]
