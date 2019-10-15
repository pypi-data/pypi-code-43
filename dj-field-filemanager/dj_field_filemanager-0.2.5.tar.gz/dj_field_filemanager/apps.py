from django.apps import AppConfig

from dj_field_filemanager.signals import attach_signals


class DjFieldFilemanagerConfig(AppConfig):
    name = 'dj_field_filemanager'
    ready_has_run = False

    def ready(self):
        if self.ready_has_run:
            return
        attach_signals()
        self.ready_has_run = True
