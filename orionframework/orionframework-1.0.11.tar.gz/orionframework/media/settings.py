import inspect

from django.conf import settings
from django.db.models import CASCADE
from django.db.models.signals import pre_delete
from django.dispatch.dispatcher import receiver

from orionframework.utils.reflection import get_class

Document = get_class(getattr(settings, "ORION_MEDIA_DOCUMENT_MODEL_CLASS"))
Image = get_class(getattr(settings, "ORION_MEDIA_IMAGE_MODEL_CLASS"))

if not Document: raise AssertionError(
    "Please specify your custom document model class (ORION_MEDIA_DOCUMENT_MODEL_CLASS via settings.py)")
if not Image: raise AssertionError(
    "Please specify your custom document model class (ORION_MEDIA_IMAGE_MODEL_CLASS via settings.py)")


@receiver(pre_delete, sender=Image)
def on_delete_image(sender, instance, **kwargs):
    instance.delete_file(instance.file)


@receiver(pre_delete, sender=Document)
def on_delete_document(sender, instance, **kwargs):
    instance.delete_file(instance.file)
