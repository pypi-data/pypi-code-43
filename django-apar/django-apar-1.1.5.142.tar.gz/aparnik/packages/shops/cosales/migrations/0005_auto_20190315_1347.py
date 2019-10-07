# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-03-15 13:47


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifiesme', '0001_initial'),
        ('sliders', '0004_sliderimage'),
        ('counters', '0002_auto_20190115_1425'),
        ('segments', '0012_auto_20181214_1330'),
        ('notifications', '0001_initial'),
        ('reviews', '0004_reviewsummary_percentage'),
        ('bookmarks', '0002_auto_20181026_1745'),
        ('buttons', '0006_auto_20190120_1724'),
        ('cosales', '0004_auto_20190315_1340'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cosalehistory',
            name='basemodel_ptr',
        ),
        migrations.RemoveField(
            model_name='cosalehistory',
            name='cosale_obj',
        ),
        migrations.RemoveField(
            model_name='cosale',
            name='status',
        ),
        migrations.DeleteModel(
            name='CoSaleHistory',
        ),
    ]
