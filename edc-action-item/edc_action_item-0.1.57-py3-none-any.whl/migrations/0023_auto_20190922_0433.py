# Generated by Django 2.2.2 on 2019-09-22 02:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("edc_action_item", "0022_auto_20190628_2136")]

    operations = [
        migrations.RemoveField(
            model_name="historicalreference", name="subject_identifier"
        ),
        migrations.RemoveField(model_name="reference", name="subject_identifier"),
    ]
