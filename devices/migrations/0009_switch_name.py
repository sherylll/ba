# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-04 10:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0008_remove_switch_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='switch',
            name='name',
            field=models.CharField(default='', max_length=200),
        ),
    ]