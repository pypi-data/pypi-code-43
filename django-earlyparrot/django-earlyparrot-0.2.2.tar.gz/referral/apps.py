from django.apps import AppConfig


class ReferralConfig(AppConfig):
    name = 'referral'
    verbose_name = 'Referral'

    def ready(self):
        from .signals import setup_signals
        setup_signals()
