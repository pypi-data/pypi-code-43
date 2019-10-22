# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from model_utils.models import TimeStampedModel

from ..conf import settings
from ..helpers import random_string


class GenericTypeformFeedback(TimeStampedModel):

    object_id = models.IntegerField(db_index=True, null=True)
    content_type = models.ForeignKey(
        ContentType,
        null=True,
        on_delete=models.CASCADE,
    )
    related_to = GenericForeignKey()

    quiz_slug = models.CharField(
        max_length=256,
        unique=True,
        default=random_string,
    )
    typeform_id = models.CharField(
        max_length=56,
        blank=True,
        null=True,
    )

    url = models.CharField(
        max_length=200,
        blank=True,
        null=True,
    )
    typeform_type = models.CharField(
        max_length=1,
        choices=settings.TYPEFORM_FEEDBACK_TYPE_CHOICES,
    )

    def __str__(self):
        return '{} - {}'.format(self.url, self.get_typeform_type_display())

    @classmethod
    def create_typeform(cls, linked_object, slug, typeform_id, *args, **kwargs):
        new_typeform = cls(
            content_type=ContentType.objects.get_for_model(linked_object),
            object_id=linked_object.pk,
            quiz_slug=slug,
            typeform_id=typeform_id,
            url=kwargs.get('url', settings.TYPEFORM_FEEDBACK_DEFAULT_URL.format(typeform_id))
        )
        new_typeform.save()
        return new_typeform

    @property
    def typeform_url(self):
        return self.url

    def set_url(self, url):
        self.url = url
        self.save(update_fields=['url', 'modified'])
