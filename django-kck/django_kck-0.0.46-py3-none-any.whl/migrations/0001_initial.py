# Generated by Django 2.2.5 on 2019-09-24 03:40

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='RefreshQueue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=1024)),
                ('hints', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('primer_name', models.CharField(db_index=True, max_length=1024)),
                ('claimant', models.CharField(blank=True, max_length=64, null=True)),
                ('claimed', models.DateTimeField(blank=True, null=True)),
                ('requested', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='DataProduct',
            fields=[
                ('key', models.CharField(max_length=1024, primary_key=True, serialize=False)),
                ('value', django.contrib.postgres.fields.jsonb.JSONField()),
                ('primer_name', models.CharField(blank=True, db_index=True, max_length=1024, null=True)),
                ('version', models.PositiveIntegerField(default=1)),
                ('modified', models.DateTimeField(auto_now_add=True)),
                ('soft_expire', models.DateTimeField(blank=True, null=True)),
                ('hard_expire', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'unique_together': {('primer_name', 'key')},
            },
        ),
    ]
