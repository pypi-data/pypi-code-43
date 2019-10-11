from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class PaycometConfig(AppConfig):
    name = 'paycomet'
    verbose_name = "PAYCOMET"

    def ready(self):
        required_settings = [
            'PAYCOMET_MERCHANT_CODE',
            'PAYCOMET_TERMINAL',
            'PAYCOMET_PASSWORD',
            'PAYCOMET_JET_ID',
        ]

        for key in required_settings:
            if not hasattr(settings, key):
                raise ImproperlyConfigured(f"{key} setting must not be empty.")
