# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-24 10:17
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0019_publisher'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publisher',
            name='sessionID',
        ),
    ]