# flake8: noqa

# Imports from Django.
from django.db import models
from django.core import serializers as django_serializers
from django.utils import timezone


# Imports from civic_utils.
from civic_utils.models.managers import CivicBaseManager
from civic_utils.models.mixins import NaturalKeyMixin
from civic_utils.utils.importers import import_class
from civic_utils.utils.rest_formats import REST_FORMAT_PARSERS
from civic_utils.utils.rest_formats import REST_FORMAT_RENDERERS


class CivicBaseModel(NaturalKeyMixin, models.Model):
    created = models.DateTimeField(editable=False)
    updated = models.DateTimeField(editable=False)

    objects = CivicBaseManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.created:
            self.created = timezone.now()
        self.updated = timezone.now()

        return super(CivicBaseModel, self).save(*args, **kwargs)

    @classmethod
    def get_default_serializer(self, format="json"):
        serializer_path = getattr(self, "default_serializer", None)

        if serializer_path and format in REST_FORMAT_RENDERERS.keys():
            serializer_klass = import_class(serializer_path)
            renderer_klass = REST_FORMAT_RENDERERS[format]

            return serializer_klass, renderer_klass

        return (django_serializers.get_serializer(format), None)

    @classmethod
    def deserialize(self, format, data_stream):
        parser_klass = REST_FORMAT_PARSERS[format]
        raw_data = parser_klass().parse(data_stream)

        serializer_path = getattr(self, "default_serializer", None)

        if serializer_path:
            serializer_klass = import_class(serializer_path)
            return serializer_klass(many=True).deserialize(raw_data)

        return list(django_serializers.python.Deserializer(raw_data))
