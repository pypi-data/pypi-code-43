# -*- coding:utf-8 -*-
from __future__ import division

from django_szuprefix.utils.statutils import do_rest_stat_action
from rest_framework.decorators import list_route, detail_route
from rest_framework.serializers import ModelSerializer

from django_szuprefix.api.mixins import UserApiMixin
from django_szuprefix_saas.saas.mixins import PartyMixin, PartySerializerMixin
from django_szuprefix_saas.saas.permissions import IsSaasWorker
from django_szuprefix_saas.school.permissions import IsStudent, IsTeacher
from .apps import Config
from rest_framework.response import Response
from rest_condition.permissions import Or

__author__ = 'denishuang'
from . import models, serializers
from rest_framework import viewsets, filters
from django_szuprefix.api.helper import register
from rest_framework import status


class PersonViewSet(PartyMixin, UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Person.objects.all()
    serializer_class = serializers.PersonSerializer
    filter_fields = ('gender',)
    search_fields = ('name',)

    def get_queryset(self):
        qset = super(PersonViewSet, self).get_queryset()
        user = self.request.user
        if user.has_perm('person.view_all_person'):
            pass
        # elif hasattr(user, 'as_school_teacher'):
        #     qset = qset.filter(teacher=user.as_school_teacher)
        else:
            qset = qset.none()
        return qset
register(Config.label, 'person', PersonViewSet)
