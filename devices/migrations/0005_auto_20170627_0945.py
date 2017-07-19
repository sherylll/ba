# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-27 09:45
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0004_auto_20170627_0755'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Owner',
        ),
        migrations.AlterModelOptions(
            name='led',
            options={'permissions': (('led_on', 'can turn on LED'), ('led_off', 'can turn off LED'))},
        ),
    ]
