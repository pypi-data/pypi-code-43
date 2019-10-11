# -*- coding:utf-8 -*- 

from rest_framework import serializers, viewsets, mixins, decorators
from . import models
from django.contrib.contenttypes.models import ContentType


class TempFileSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.TempFile
        fields = ('url', 'name', 'file', 'id')


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Image
        fields = ('content_type', 'object_id', 'file', 'id')


class ContenttypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ("app_label", 'model', 'name', '__str__', 'id')
