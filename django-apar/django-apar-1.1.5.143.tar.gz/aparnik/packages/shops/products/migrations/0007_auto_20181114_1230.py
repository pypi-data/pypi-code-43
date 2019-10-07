# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-11-14 12:30


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('filefields', '0004_filefield_title'),
        ('products', '0006_auto_20181113_1848'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductProperty',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('icon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='filefields.FileField', verbose_name='Icon')),
            ],
            options={
                'verbose_name': 'Product Property',
                'verbose_name_plural': 'Product Properties',
            },
        ),
        migrations.CreateModel(
            name='ProductPropertyMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255, verbose_name='Content')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.Product', verbose_name='Product')),
                ('property', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='products.ProductProperty', verbose_name='Property')),
            ],
            options={
                'verbose_name': 'Product Property Membership',
                'verbose_name_plural': 'Product Property Membership',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='properties',
            field=models.ManyToManyField(through='products.ProductPropertyMembership', to='products.ProductProperty', verbose_name='Product Properties'),
        ),
    ]
