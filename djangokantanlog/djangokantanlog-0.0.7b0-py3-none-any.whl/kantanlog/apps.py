from django.apps import AppConfig


class KantanlogConfig(AppConfig):

    name = 'kantanlog'

    def ready(self):
        from . import signals # noqa
