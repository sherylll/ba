# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-18 11:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('devices', '0017_auto_20170718_1010'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='uid',
            field=models.CharField(max_length=20, null=True),
        ),
    ]