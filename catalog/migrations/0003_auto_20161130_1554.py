# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-30 07:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0002_bookinstance_borrower'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookinstance',
            options={'permissions': (('can_mark_returned', 'Set book as returned'),)},
        ),
    ]
