# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2019-10-06 11:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('school', '0025_auto_20190809_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clazz',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='classes', related_query_name='class', to='school.Student', verbose_name='\u5b66\u751f'),
        ),
        migrations.AlterField(
            model_name='student',
            name='create_time',
            field=models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='\u521b\u5efa\u65f6\u95f4'),
        ),
    ]
