# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-03-12 21:44
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('budget', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventBase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.CharField(blank=True, default='', max_length=200, null=True)),
                ('budget', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='budget.Budget')),
            ],
        ),
        migrations.RemoveField(
            model_name='expense',
            name='budget',
        ),
        migrations.RemoveField(
            model_name='expense',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='expense',
            name='id',
        ),
        migrations.RemoveField(
            model_name='income',
            name='budget',
        ),
        migrations.RemoveField(
            model_name='income',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='income',
            name='id',
        ),
        migrations.RemoveField(
            model_name='moneytransfer',
            name='budget',
        ),
        migrations.RemoveField(
            model_name='moneytransfer',
            name='comment',
        ),
        migrations.RemoveField(
            model_name='moneytransfer',
            name='id',
        ),
        migrations.AddField(
            model_name='expense',
            name='eventbase_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='budget.EventBase'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='income',
            name='eventbase_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='budget.EventBase'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='journalrecord',
            name='event',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='budget.EventBase'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='moneytransfer',
            name='eventbase_ptr',
            field=models.OneToOneField(auto_created=True, default=1, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='budget.EventBase'),
            preserve_default=False,
        ),
    ]
