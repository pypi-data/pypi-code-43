# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2018-12-03 13:27


from django.db import migrations

def empty_table(apps, schema_editor):
    '''
    We can't import the Post model directly as it may be a newer
    version than this migration expects. We use the historical version.
    '''
    SocialNetwork = apps.get_model('socials', 'SocialNetwork')
    SocialNetwork.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('socials', '0002_socialnetworksegment'),
    ]

    operations = [
        migrations.RunPython(empty_table, reverse_code=migrations.RunPython.noop),
    ]
