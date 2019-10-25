# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sample', models.FileField(upload_to='%Y/%m/%d/samples/', verbose_name='Sample')),
                ('klass_id', models.CharField(max_length=100, null=True, verbose_name='Class ID', blank=True)),
                ('klass', models.CharField(max_length=100, null=True, verbose_name='Class', blank=True)),
                ('features', models.CharField(max_length=100, null=True, verbose_name='Features', blank=True)),
                ('codes', models.TextField(null=True, verbose_name='Codes', blank=True)),
                ('data', models.FileField(upload_to='%Y/%m/%d/data/', null=True, verbose_name='Data', blank=True)),
                ('scale', models.BooleanField(default=False, verbose_name='Scale')),
                ('balance', models.BooleanField(default=False, verbose_name='Balance')),
                ('reduction', models.CharField(max_length=100, null=True, verbose_name='Reduction', blank=True)),
                ('ncomp', models.IntegerField(null=True, verbose_name='Ncomp', blank=True)),
                ('separability', models.BooleanField(default=False, verbose_name='Separability')),
                ('treatment_type', models.CharField(default='classification', max_length=100, verbose_name='Treatment type')),
                ('distance', models.CharField(default='euclidian', max_length=100, verbose_name='Distance algorythm')),
                ('algorythm', models.CharField(max_length=100, null=True, verbose_name='Algorythm(s)', blank=True)),
                ('optimisation', models.BooleanField(default=False, verbose_name='Optimisation')),
                ('prediction', models.BooleanField(default=True, verbose_name='Prediction')),
                ('job_status', models.CharField(default='Q', max_length=2, verbose_name='Status', choices=[('Q', 'Queued'), ('P', 'Processing'), ('D', 'Done')])),
                ('added', models.DateTimeField(auto_now_add=True, verbose_name='Added')),
                ('config_filepath', models.CharField(max_length=1000, null=True, verbose_name='Config filepath', blank=True)),
                ('output_path', models.CharField(max_length=1000, null=True, verbose_name='Output path', blank=True)),
            ],
            options={
                'ordering': ('-added',),
            },
        ),
    ]
