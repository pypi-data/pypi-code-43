# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django_szuprefix.api.mixins import UserApiMixin
from django_szuprefix_saas.saas.mixins import PartyMixin
from django_szuprefix_saas.saas.permissions import IsSaasWorker

from . import serializers, models
from rest_framework import viewsets
from django_szuprefix.api.helper import register

__author__ = 'denishuang'


class CommentViewSet(PartyMixin, UserApiMixin, viewsets.ModelViewSet):
    serializer_class = serializers.CommentSerializer
    queryset = models.Comment.objects.all()
    permission_classes = [IsSaasWorker]
    filter_fields = {
        'content_type__app_label': ['exact'],
        'content_type__model': ['exact'],
        'user': ['exact']
    }

    def get_queryset(self):
        qset = super(CommentViewSet, self).get_queryset()
        user = self.request.user
        if user.has_perm('school.view_all_comment'):
            pass
        else:
            qset = qset.filter(user=user)
        return qset


register(__package__, 'comment', CommentViewSet)
