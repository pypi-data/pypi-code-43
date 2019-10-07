# Generated by Django 2.1.8 on 2019-05-02 04:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("authorizations", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="AuthorizationsConfig",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("api_root", models.URLField(unique=True, verbose_name="api root")),
                (
                    "component",
                    models.CharField(
                        choices=[
                            ("ZRC", "ZRC"),
                            ("ZTC", "ZTC"),
                            ("DRC", "DRC"),
                            ("BRC", "BRC"),
                            ("NC", "NC"),
                            ("AC", "AC"),
                        ],
                        default="ZRC",
                        max_length=50,
                        verbose_name="component",
                    ),
                ),
            ],
            options={"verbose_name": "Autorisatiecomponentconfiguratie"},
        )
    ]
