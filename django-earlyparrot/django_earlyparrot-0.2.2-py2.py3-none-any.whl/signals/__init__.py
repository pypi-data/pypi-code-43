from django.apps import apps
from django.db import models


from .subscriber import new_subscriber


def setup_signals():
    Subscriber = apps.get_model(
        app_label='referral',
        model_name='Subscriber',
    )

    models.signals.post_save.connect(new_subscriber, sender=Subscriber)
