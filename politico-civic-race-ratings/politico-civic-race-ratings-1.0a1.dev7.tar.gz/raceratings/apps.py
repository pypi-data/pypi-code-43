# Imports from Django.
from django.apps import AppConfig


class RaceratingsConfig(AppConfig):
    name = "raceratings"

    def ready(self):
        from raceratings import signals  # noqa
