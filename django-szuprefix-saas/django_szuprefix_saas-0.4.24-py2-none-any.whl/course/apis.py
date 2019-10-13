# -*- coding:utf-8 -*-
from django_szuprefix.utils.statutils import do_rest_stat_action
from rest_framework.decorators import list_route, detail_route
from django_szuprefix_saas.saas.mixins import PartyMixin
from django_szuprefix_saas.school.permissions import IsStudent, IsTeacher
from .apps import Config

__author__ = 'denishuang'
from . import models, serializers, stats
from rest_framework import viewsets, response
from django_szuprefix.api.helper import register


class CourseViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Course.objects.all()
    serializer_class = serializers.CourseSerializer
    search_fields = ('name', 'code')
    filter_fields = {
        'id': ['exact', 'in'],
        'is_active': ['exact'],
        'name': ['exact'],
        'category': ['exact'],
        'code': ['exact']
    }
    ordering_fields = ('is_active', 'title', 'create_time')

    def get_queryset(self):
        qset = super(CourseViewSet, self).get_queryset()
        user = self.request.user
        if user.has_perm('course.view_all_course'):
            pass
        elif hasattr(user, 'as_school_student'):
            student = user.as_school_student
            # from django.db.models import Q
            # qset = qset.filter(Q(school_students=student) | Q(school_classes=student.clazz)).filter(is_active=True).distinct()
            qset = student.all_courses
        elif hasattr(user, 'as_school_teacher'):
            qset = qset.filter(clazz_course_relations__teacher_id=user.as_school_teacher.id).filter(
                is_active=True).distinct()
        else:
            qset = qset.none()
        return qset

    @list_route(['get'])
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_course)


register(Config.label, 'course', CourseViewSet)


class CategoryViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer
    search_fields = ('name', 'code')
    filter_fields = ('code', 'name')


register(Config.label, 'category', CategoryViewSet)


class ChapterViewSet(PartyMixin, viewsets.ModelViewSet):
    queryset = models.Chapter.objects.all()
    serializer_class = serializers.ChapterSerializer
    search_fields = ('name', 'code')
    filter_fields = {
        'id': ['exact', 'in'],
        'course': ['exact']
    }

register(Config.label, 'chapter', ChapterViewSet)
