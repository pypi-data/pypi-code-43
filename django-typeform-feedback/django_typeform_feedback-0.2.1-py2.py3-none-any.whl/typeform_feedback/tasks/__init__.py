from celery import current_app as app

from .mixin import TypeformWebhookMixin     # noqa
from .generic_typeform import UpdateGenericTypeformTask


app.tasks.register(UpdateGenericTypeformTask())
