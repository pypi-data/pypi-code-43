from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class ContactConfig(AppConfig):
    name = 'djtools.contact'
    label = 'djtools.contact'
    verbose_name = 'Contact'

    def ready(self):
        if not hasattr(settings, 'DJTOOLS_CONTACT_SITE_DOMAIN'):
            raise ImproperlyConfigured(
                "The DJTOOLS_CONTACT_SITE_DOMAIN setting must not be empty."
            )
        if not hasattr(settings, 'DJTOOLS_CONTACT_MAIL_FROM'):
            raise ImproperlyConfigured(
                "The DJTOOLS_CONTACT_MAIL_FROM setting must not be empty."
            )
        if not hasattr(settings, 'DJTOOLS_CONTACT_MAIL_TO'):
            raise ImproperlyConfigured(
                "The DJTOOLS_CONTACT_MAIL_TO setting must not be empty."
            )
