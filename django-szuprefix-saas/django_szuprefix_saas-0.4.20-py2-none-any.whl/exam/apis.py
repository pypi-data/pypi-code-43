# -*- coding:utf-8 -*-
from __future__ import division

from django_szuprefix.utils.statutils import do_rest_stat_action
from rest_framework.decorators import list_route, detail_route

from django_szuprefix.api.mixins import UserApiMixin
from django_szuprefix_saas.saas.mixins import PartyMixin
from django_szuprefix_saas.saas.permissions import IsSaasWorker
from django_szuprefix_saas.school.permissions import IsStudent, IsTeacher
from .apps import Config
from rest_framework.response import Response
from rest_condition.permissions import Or

__author__ = 'denishuang'
from . import models, serializers, stats
from rest_framework import viewsets, exceptions
from django_szuprefix.api.helper import register
from rest_framework import status


class PaperViewSet(PartyMixin, UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Paper.objects.all()
    serializer_class = serializers.PaperFullSerializer
    search_fields = ('title',)
    filter_fields = {
        'id': ['in', 'exact'],
        'is_active': ['exact'],
        'is_break_through': ['exact'],
        # 'course_courses': ['exact'],
        # 'course_chapters': ['exact'],
        # 'course_courses__school_teachers': ['exact'],
        # 'course_chapters__course__school_teachers': ['exact'],
        # 'course_courses__school_classes': ['exact'],
        'owner_type': ['exact'],
        'owner_id': ['exact'],
    }
    ordering_fields = ('is_active', 'title', 'create_time')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.PaperSerializer
        return super(PaperViewSet, self).get_serializer_class()

    def get_queryset(self):
        qset = super(PaperViewSet, self).get_queryset()
        user = self.request.user
        if user.has_perm('exam.view_all_paper'):
            pass
        elif hasattr(user, 'as_school_teacher'):
            qset = user.as_school_teacher.exam_papers
        elif hasattr(user, 'as_school_student'):
            qset = user.as_school_student.exam_papers
        else:
            qset = qset.none()
        return qset

    @detail_route(['post'], permission_classes=[IsSaasWorker])
    def answer(self, request, pk=None):
        paper = self.get_object()
        serializer = serializers.AnswerSerializer(data=request.data, party=self.party)
        if serializer.is_valid():
            answer = serializer.save(user=self.request.user, paper=paper)
            headers = self.get_success_headers(serializer.data)
            data = serializer.data
            data['is_passed'] = answer.performance.get('stdScore') >= models.EXAM_MIN_PASS_SCORE
            return Response(data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @list_route(['POST'])
    def batch_active(self, request):
        rows = self.get_queryset() \
            .filter(id__in=request.data.get('id__in', [])) \
            .update(is_active=request.data.get('is_active', True))
        return Response({'rows': rows})

    @list_route(['get'], permission_classes=[Or(IsStudent, IsTeacher)])
    def for_course(self, request):
        course_id = request.query_params.get("id")
        course = self.party.course_courses.filter(id=course_id).first()
        if not course:
            raise exceptions.NotFound
        serializer = serializers.CoursePaperSerializer(course)
        from django.forms import model_to_dict
        c = serializer.data
        unlock = False
        user = request.user

        def fill_papers(papers, unlock=False):
            pids = [p.get('id') for p in papers]
            pfs = user.exam_performances.filter(paper_id__in=pids)
            pfm = dict([(p.paper_id, p) for p in pfs])
            for p in papers:
                performance = pfm.get(p['id'])
                ibt = p.get('is_break_through')
                if ibt:
                    if (performance is None or performance.is_passed == False) and unlock is False:
                        unlock = True
                        p['lock'] = 'unlock'
                    elif performance is not None and performance.is_passed == True:
                        p['lock'] = None
                    else:
                        p['lock'] = 'lock'
                else:
                    p['lock'] = None

                # if p.get('is_break_through') and unlock is False and (
                #                 performance is None or performance.is_passed == False):
                #     unlock = True
                #     p['unlock'] = True
                p['performance'] = model_to_dict(performance, ['score', 'detail', 'is_passed']) if performance else None
            return unlock

        for cpt in c['chapters']:
            unlock = fill_papers(cpt['exam_papers'], unlock)
        fill_papers(c['exam_papers'])
        return Response(dict(course=c))


    @detail_route(methods=['get'])
    def my_performance(self, request, pk):
        paper = self.get_object()
        performance = request.user.exam_performances.filter(paper=paper).first()
        serializer = serializers.PerformanceSerializer(performance)
        return Response(serializer.data)


register(Config.label, 'paper', PaperViewSet)


class AnswerViewSet(PartyMixin, UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Answer.objects.all()
    serializer_class = serializers.AnswerSerializer
    filter_fields = ('paper', 'user')

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.AnswerListSerializer
        return super(AnswerViewSet, self).get_serializer_class()

    def get_queryset(self):
        qset = super(AnswerViewSet, self).get_queryset()
        user = self.request.user
        pms = self.request.query_params
        students = None
        if pms.get('clazz'):
            students = self.party.school_students.filter(clazz_id=pms.get('clazz'))
        if user.has_perm('exam.view_all_answer'):
            pass
        elif hasattr(user, 'as_school_student'):
            qset = qset.filter(user_id=user.id)
        elif hasattr(user, 'as_school_teacher'):
            students = user.as_school_teacher.students
            if pms.get('clazz'):
                students = students.filter(class_id=pms.get('clazz'))
        else:
            qset = qset.none()
        if students is not None:
            qset = qset.filter(user_id__in=list(students.values_list('user_id', flat=True)))
        return qset

    @list_route(['get'])
    def stat(self, request):
        return do_rest_stat_action(self, stats.stats_answer)


register(Config.label, 'answer', AnswerViewSet)


class StatViewSet(PartyMixin, UserApiMixin, viewsets.ReadOnlyModelViewSet):
    queryset = models.Stat.objects.all()
    serializer_class = serializers.StatSerializer
    filter_fields = ('paper',)


register(Config.label, 'stat', StatViewSet)


class PerformanceViewSet(PartyMixin, UserApiMixin, viewsets.ModelViewSet):
    queryset = models.Performance.objects.all()
    serializer_class = serializers.PerformanceSerializer
    filter_fields = ('paper',)
    search_fields = ('paper__title',)
    ordering_fields = ('score', 'update_time')

    def filter_queryset(self, queryset):
        qset = super(PerformanceViewSet, self).filter_queryset(queryset)
        ids = self.request.query_params.get("papers")
        # qset = qset.filter(user=self.request.user)
        if ids:
            qset = qset.filter(paper_id__in=[int(id) for id in ids.split(",")])
        return qset

    def get_queryset(self):
        qset = super(PerformanceViewSet, self).get_queryset()
        user = self.request.user
        pms = self.request.query_params
        students = None
        if pms.get('clazz'):
            students = self.party.school_students.filter(clazz_id=pms.get('clazz'))
        if user.has_perm('exam.view_all_answer'):
            pass
        elif hasattr(user, 'as_school_student'):
            qset = qset.filter(user_id=user.id)
        elif hasattr(user, 'as_school_teacher'):
            students = user.as_school_teacher.students
            if pms.get('clazz'):
                students = students.filter(clazz_id=pms.get('clazz'))
        else:
            qset = qset.none()
        if students is not None:
            qset = qset.filter(user_id__in=list(students.values_list('user_id', flat=True)))
        return qset


register(Config.label, 'performance', PerformanceViewSet)
