from django.apps import AppConfig
from django.conf import settings


class DeepPagesConfig(AppConfig):
    name = 'deeppages'
    verbose_name = 'Django Deep Pages'

    def ready(self):
        if not hasattr(settings, 'AUTOSLUG_SLUGIFY_FUNCTION'):
            setattr(settings,
                    'AUTOSLUG_SLUGIFY_FUNCTION',
                    'autoslug.settings.slugify')
