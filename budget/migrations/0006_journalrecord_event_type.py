# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-19 18:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0005_acc_is_archived'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalrecord',
            name='event_type',
            field=models.CharField(blank=True, default='', max_length=200, null=True),
        ),
    ]
