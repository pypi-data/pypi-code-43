import sys

from django.apps import AppConfig
from django.db.models.signals import post_migrate

from redmin.management import init_models


class RedminConfig(AppConfig):
    name = 'redmin'

    def ready(self):
        post_migrate.connect(init_models)

