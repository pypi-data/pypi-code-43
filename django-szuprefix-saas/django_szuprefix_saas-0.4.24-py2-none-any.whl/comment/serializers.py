# -*- coding:utf-8 -*-
from django_szuprefix.api.mixins import IDAndStrFieldSerializerMixin
from django_szuprefix_saas.saas.mixins import PartySerializerMixin
from rest_framework import serializers
from . import models


class CommentSerializer(IDAndStrFieldSerializerMixin, PartySerializerMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = ('content_type', 'object_id', 'object_name', 'user', 'content', 'is_active')
        read_only_fields = ('user', )
