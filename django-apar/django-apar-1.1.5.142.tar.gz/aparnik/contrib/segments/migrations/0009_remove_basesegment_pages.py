# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-12-13 18:46


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('segments', '0008_auto_20181213_1845'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basesegment',
            name='pages',
        ),
    ]
