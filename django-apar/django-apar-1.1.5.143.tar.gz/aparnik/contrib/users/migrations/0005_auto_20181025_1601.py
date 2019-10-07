# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-10-25 16:01


import aparnik.utils.fields
import django.core.validators
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('aparnik_users', '0004_auto_20180814_0159'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='avatar',
        ),
        migrations.AlterField(
            model_name='user',
            name='username',
            field=aparnik.utils.fields.PhoneField(max_length=30, unique=True, validators=[
                django.core.validators.RegexValidator(code=b'nomatch',
                                                      message='phone is not valid, please insert with code',
                                                      regex=b'^0(?!0)\\d{2}([0-9]{8})$')], verbose_name='Mobile'),
        ),
        migrations.AddField(
            model_name='user',
            name='wallet',
            field=aparnik.utils.fields.PriceField(decimal_places=0, default=0, max_digits=20, verbose_name='Wallet'),
        ),
    ]
