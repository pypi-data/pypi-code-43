# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
from django.shortcuts import render, reverse, redirect
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q, F, Sum, Count
from django.db.models import Case, When, Value, CharField
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse_lazy
from dss.Serializer import serializer
from django.apps import apps
from django.db import connection
from django.contrib import messages

from .utils import export_csv, get_user_name
from .dt import get_year_month_week, get_datetime_with_scope_offset
from .models import ClassWeek, MentorScoreWeek
from .exports import ClassWeekReport, get_section_name, get_class_name
from .forms import MentorScoreWeekForm, UserServerForm, UserSectionForm, Report
from bee_django_course.exports import get_teach_users

User = get_user_model()


# from django.
# Create your views here.
def test(request):
    MentorScoreWeek.update_rank(2018, 26)
    return render(request, 'bee_django_report/report/pie.html', {"title": "统计模版", "subtext": '模拟数据', "data_list": []})


class IndexView(TemplateView):
    template_name = 'bee_django_report/index.html'


class UserGenderView(TemplateView):
    template_name = 'bee_django_report/report/pie.html'
    user_app = 'bee_django_user'
    user_model = 'UserProfile'
    gender_field = 'preuser__gender'
    condition_list = None  # 格式：[{"key": "name", "value": "bee"}]
    gender_list = ((0, "无"), (1, "男"), (2, "女"))
    case_list = [When(preuser__gender=item[0], then=Value(item[1])) for i, item in enumerate(gender_list)]

    def get_context_data(self, **kwargs):
        context = super(UserGenderView, self).get_context_data(**kwargs)
        context["title"] = '学员性别'
        context["subtext"] = ''
        context["data_list"] = self.get_date_list()

        return context

    def get_date_list(self):

        app = apps.get_app_config(self.user_app)
        model = app.get_model(self.user_model)
        kwargs = {}  # 动态查询的字段
        if self.condition_list:
            for i, value in enumerate(self.condition_list):
                kwargs[value["key"]] = value["value"]
        queryset = model.objects.filter(**kwargs).values(self.gender_field).order_by(self.gender_field) \
            .annotate(value=Count(1)) \
            .annotate(name=Case(*self.case_list, default=Value('未填写'), output_field=CharField()))

        return serializer(queryset, output_type='json')


class UserAgeView(TemplateView):
    template_name = 'bee_django_report/report/pie.html'

    def get_sql_str(self):
        sql = '''
        SELECT COUNT(C.age_group), C.age_group FROM
        (SELECT
          CASE
            WHEN B.age >= 50 THEN '50以上'
            WHEN B.age >= 40 THEN '40-50'
            WHEN B.age >= 30 THEN '30-40'
            WHEN B.age >= 20 THEN '20-30'
            WHEN B.age < 20 THEN '20以下'
            ELSE '无'
          END AS age_group
        FROM
        (SELECT (A.this_year - A.birth_year) AS age
        FROM
        (SELECT EXTRACT(YEAR FROM CURRENT_DATE) AS this_year, EXTRACT(YEAR FROM "bee_django_crm_preuser".birthday) AS birth_year
        FROM "bee_django_user_profile" INNER JOIN "bee_django_crm_preuser" ON "bee_django_user_profile".preuser_id = "bee_django_crm_preuser".id) AS A) AS B ) AS C GROUP BY C.age_group
        '''

        return sql

    def get_context_data(self, **kwargs):
        context = super(UserAgeView, self).get_context_data(**kwargs)
        context["title"] = '学员年龄'
        context["subtext"] = ''
        context["data_list"] = self.get_date_list()

        return context

    def get_date_list(self):
        with connection.cursor() as cursor:
            cursor.execute(self.get_sql_str())
            data = cursor.fetchall()
        rc = []
        for i in data:
            rc.append({"name": i[1], "value": i[0]})
        return json.dumps(rc)

        # return [
        #     {"name": 'A1', "value": 12121},
        #     {"name": 'B1', "value": 23231},
        #     {"name": 'C1', "value": 19191}
        # ]


class UserSectionList(ListView):
    model = User
    template_name = 'bee_django_report/report/user/user_section_list.html'
    context_object_name = 'user_list'
    paginate_by = 20
    queryset = None

    def get_context_data(self, **kwargs):
        context = super(UserSectionList, self).get_context_data(**kwargs)
        status = self.request.GET.get("status")
        class_id = self.request.GET.get("user_class")
        assistant_id = self.request.GET.get("assistant")
        expire_date_start = self.request.GET.get("expire_date_start")
        expire_date_end = self.request.GET.get("expire_date_end")

        context["search_form"] = UserSectionForm(
            data={"status": status, "user_class": class_id, "assistant": assistant_id,
                  "expire_date_start": expire_date_start,
                  "expire_date_end": expire_date_end}, user=self.request.user)
        return context

    def get_user_list(self):
        status = self.request.GET.get("status")
        class_id = self.request.GET.get("user_class")
        assistant_id = self.request.GET.get("assistant")
        expire_date_start = self.request.GET.get("expire_date_start")
        expire_date_end = self.request.GET.get("expire_date_end")
        queryset = self.request.user.get_student_list().order_by("userprofile__expire_date")
        if not status in [0, "0", None, '']:
            if status == "1":  # 正常
                queryset = queryset.filter(is_active=True, userprofile__is_pause=False).exclude(
                    userleavestatus__status=1)
        if not class_id in [0, "0", None, '']:
            queryset = queryset.filter(userprofile__user_class_id=class_id)

        if not assistant_id in [0, "0", None, '']:
            queryset = queryset.filter(userprofile__user_class__assistant_id=assistant_id)

        if expire_date_start:
            queryset = queryset.filter(userprofile__expire_date__gte=expire_date_start)
        if expire_date_end:
            queryset = queryset.filter(userprofile__expire_date__lte=expire_date_end)
        return queryset

    def get_user_current_course(self, user):
        user_course_section = Report.get_user_current_course_section(user)
        return user_course_section

    def get_user_current_course_name(self, ucs):
        if ucs:
            return ucs.user_course.course.name
        else:
            return ""

    def get_user_current_section(self, user):
        user_course_section = Report.get_user_current_course_section(user)
        return user_course_section

    def get_user_current_section_name(self, user_section):
        if user_section:
            return user_section.section.name
        else:
            return ""

    def get_user_section_progress(self, user):
        user_course_section = Report.get_user_current_course_section(user)
        if user_course_section:
            total_count = user_course_section.user_course.course.coursesectionmid_set.all().count()
            _list = Report.get_user_pass_section_list(user_course_section.user_course)
            pass_count = _list.count()
            return pass_count.__str__() + "/" + total_count.__str__()
        else:
            return ""

    def get_user_punch(self, user):
        user_course_section = Report.get_user_current_course_section(user)
        if user_course_section:
            user_punch = user_course_section.get_course_punch()
        else:
            return ''
        if user_punch:
            return user_punch.__str__() + '/' + user_course_section.get_punch().__str__()
        else:
            return ''

    def get_user_section_live_progress(self, user):
        user_course_section = Report.get_user_current_course_section(user)
        if user_course_section and user_course_section.section.has_videowork==True:
            return user_course_section.work_time.__str__()+ "/" +user_course_section.section.video_length_req.__str__()
        else:
            return ""

    def get_user_section_img_progress(self, user):
        user_course_section = Report.get_user_current_course_section(user)
        if user_course_section and user_course_section.section.has_imagework:
            return user_course_section.get_assignment_img_count().__str__()+ "/" +user_course_section.section.image_count_req.__str__()
        else:
            return ""

    def get_csv_info(self, user):
        return [
            user.userprofile.get_sn(),
            get_user_name(user).encode('utf-8'),
            user.userprofile.get_expire_date_str(timezone=False),
            self.get_user_current_course_name(self.get_user_current_course(user)).encode('utf-8'),
            self.get_user_current_section_name(self.get_user_current_section(user)).encode('utf-8'),
            self.get_user_section_progress(user).encode('utf-8'),
            self.get_user_punch(user).encode('utf-8'),
            self.get_user_section_live_progress(user).encode('utf-8'),
            self.get_user_section_img_progress(user).encode('utf-8')

            # str(user.userprofile.expire_date).encode('utf-8') if user.userprofile.expire_date else None

        ]

    def get_csv_headers(self):
        return [
            '序号'.encode('utf-8'),
            '缦客号'.encode('utf-8'),
            '姓名'.encode('utf-8'),
            '结课日期'.encode('utf-8'),
            '课程'.encode('utf-8'),
            '课件'.encode('utf-8'),
            '进度'.encode('utf-8'),
            '打卡'.encode('utf-8'),
            '录播'.encode('utf-8'),
            '图片'.encode('utf-8'),
        ]

    def get(self, request, *args, **kwargs):
        # print('get')
        self.queryset = self.get_user_list()
        if request.GET.get("export"):
            rows = ([(i + 1).__str__()] + self.get_csv_info(user) for i, user in enumerate(self.queryset))
            return export_csv('学生课程进度报表'.encode('utf-8'), self.get_csv_headers(), rows)
        else:
            return super(UserSectionList, self).get(request, *args, **kwargs)


class ClassWeekView(TemplateView):
    template_name = 'bee_django_report/report/class/week.html'

    def get_offset(self):
        offset = self.request.GET.get("offset")
        if not offset:
            offset = -1
        return int(offset)

    def check_save(self):
        class_id = self.kwargs["class_id"]
        ClassWeekReport().auto_save_db(class_id=class_id, offset=self.get_offset())

    def get_data(self):
        self.check_save()
        class_id = self.kwargs["class_id"]
        offset = self.get_offset()
        start_dt, end_dt = get_datetime_with_scope_offset("week", offset)
        year, month, week = get_year_month_week(start_dt)
        records = ClassWeek.objects.filter(class_id=class_id, year=year, week=week)
        return records, class_id, year, week, start_dt, end_dt, offset

    def get_context_data(self, **kwargs):
        context = super(ClassWeekView, self).get_context_data(**kwargs)
        records, class_id, year, week, start_dt, end_dt, offset = self.get_data()
        context["records"] = records
        context["class_id"] = class_id
        context["year"] = year
        context["week"] = week
        context["start_dt"] = start_dt
        context["end_dt"] = end_dt
        context["prev_week"] = offset - 1
        if offset < -1:
            context["next_week"] = offset + 1
        return context

    def get_export_user_name(self, record):
        if record.type_int == 1:
            return '共计'
        if record.type_int == 2:
            return '平均'
        if record.type_int == 3:
            return get_user_name(record.user)
        if record.type_int == 9:
            return '助教：' + get_user_name(record.mentor)

    def get(self, request, *args, **kwargs):
        if request.GET.get("export"):
            records, class_id, year, week, start_dt, end_dt, offset = self.get_data()
            rows = ([
                (i + 1).__str__(),
                self.get_export_user_name(record).encode('utf-8'),
                get_section_name(record.last_user_section_id).encode('utf-8'),
                record.live_mins,
                record.live_days,
                record.live_count,
                record.feed_count,

            ] for i, record in enumerate(records))
            headers = [
                '序号'.encode('utf-8'),
                '姓名'.encode('utf-8'),
                '进度'.encode('utf-8'),
                '练习分钟'.encode('utf-8'),
                '练习天数'.encode('utf-8'),
                '练习次数'.encode('utf-8'),
                '日志数'.encode('utf-8'),
            ]
            class_name = get_class_name(class_id)
            csv_name = "[" + class_name + "]" + year.__str__() + "年第" + week.__str__() + "周报表"
            return export_csv(csv_name.encode('utf-8'), headers, rows)
        else:
            return super(ClassWeekView, self).get(request, *args, **kwargs)


# ==========助教周评分===========
class MentorScoreList(ListView):
    template_name = 'bee_django_report/mentor_score/list.html'
    context_object_name = 'score_list'
    paginate_by = 20
    queryset = None

    # def get(self, request, *args, **kwargs):
    #     year, week = self.get_year_week()
    #     if year and week:
    #         MentorScoreWeek.update_rank(year, week)
    #         messages.success(self.request, '已更新排名')
    #     return super(MentorScoreList,self).get(request, *args)

    def get_user(self):
        user_id = self.kwargs["user_id"]
        if not user_id in [0, None]:
            try:
                mentor = User.objects.get(id=user_id)
                return mentor
            except:
                pass
        return None

    def get_year_week(self):
        year = self.request.GET.get("year")
        week = self.request.GET.get("week")
        return year, week

    def get_queryset(self):
        queryset = MentorScoreWeek.objects.all()
        mentor = self.get_user()
        if mentor:
            queryset = queryset.filter(mentor=mentor).order_by('-year', 'week')
        year, week = self.get_year_week()
        if year:
            queryset = queryset.filter(year=year)
        if week:
            queryset = queryset.filter(week=week).order_by('-score')
        return queryset

    def get_context_data(self, **kwargs):
        context = super(MentorScoreList, self).get_context_data(**kwargs)
        mentor = self.get_user()
        year, week = self.get_year_week()
        if mentor:
            context["mentor"] = mentor
        if year:
            context["year"] = year
        if week:
            context["week"] = week
        return context


class MentorScoreCreate(CreateView):
    model = MentorScoreWeek
    form_class = MentorScoreWeekForm
    template_name = 'bee_django_report/mentor_score/form.html'

    def get_success_url(self):
        return reverse_lazy('bee_django_report:mentor_score_list', kwargs=self.kwargs)

    def form_valid(self, form):
        # form.instance.mentor_id = self.kwargs["user_id"]
        record = form.save(commit=False)
        record.mentor_id = self.kwargs["user_id"]
        record.save()
        MentorScoreWeek.update_rank(record.year, record.week)
        # return super(MentorScoreCreate, self).form_valid(form)
        return redirect(reverse_lazy('bee_django_report:mentor_score_list', kwargs=self.kwargs))


class MentorScoreUpdate(UpdateView):
    model = MentorScoreWeek
    form_class = MentorScoreWeekForm
    template_name = 'bee_django_report/mentor_score/form.html'

    def form_valid(self, form):
        pk = self.kwargs["pk"]
        try:
            old = MentorScoreWeek.objects.get(id=pk)
        except:
            old = None
        record = form.save(commit=True)
        if old:
            MentorScoreWeek.update_rank(old.year, old.week)
        MentorScoreWeek.update_rank(record.year, record.week)
        return redirect(reverse_lazy('bee_django_report:mentor_score_list', kwargs={"user_id": 0}))

        # def get_context_data(self, **kwargs):
        #     context = super(MentorScoreUpdate, self).get_context_data(**kwargs)
        #     context["source"] = Source.objects.get(id=self.kwargs["pk"])
        #     return context


class MentorScoreDelete(DeleteView):
    model = MentorScoreWeek
    success_url = None

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        record = self.get_object()
        record.delete()
        MentorScoreWeek.update_rank(record.year, record.week)
        return redirect(reverse_lazy('bee_django_report:mentor_score_list', kwargs={"user_id": 0}))


# 班级学习进度 准备弃用，功能类似于UserSectionList
class UserClassProgress(TemplateView):
    template_name = "bee_django_report/report/class/progress.html"

    def get_users(self):
        try:
            from bee_django_user.models import UserClass
            class_id = self.kwargs["class_id"]
            user_class = UserClass.objects.get(id=class_id)
            return user_class.get_students()

        except:
            return []

    # 获取最后一个学到的课件
    def get_last_section(self, user):
        try:
            from bee_django_course.exports import get_user_last_course_section
            ucs = get_user_last_course_section(user)
            return ucs
        except:
            return None

    def get_context_data(self, **kwargs):
        context = super(UserClassProgress, self).get_context_data(**kwargs)
        users = self.get_users()
        data_list = []
        for user in users:
            data = {}
            data["user"] = user
            ucs = self.get_last_section(user)
            if ucs:
                data["ucs_id"] = ucs.id
                data["ucs"] = ucs
                data["section_has_videowork"] = ucs.section.has_videowork
                data["section_video_length_req"] = ucs.section.video_length_req
                data["ucs_work_time"] = ucs.work_time
            data_list.append(data)
        context["data_list"] = data_list
        return context


# 查看客服管理的助教报表
class ServerAssistantView(TemplateView):
    template_name = 'bee_django_report/report/user/server_assistant_list.html'

    # def get(self, request, *args, **kwargs):
    #     return

    def get_assistant_list(self):
        server_id = self.request.GET.get("server")
        status = self.request.GET.get("status")

        if server_id in ["", 0, None, '']:
            return None
        else:
            queryset = User.objects.filter(userprofile__agent__user_id=server_id)

        if not status in [0, "0", None, '']:
            if status == "1":  # 正常
                queryset = queryset.filter(is_active=True, userprofile__is_pause=False).exclude(
                    userleavestatus__status=1)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(ServerAssistantView, self).get_context_data(**kwargs)
        server_id = self.request.GET.get("server")
        status = self.request.GET.get("status")
        context["server_form"] = UserServerForm(data={"status": status, "server": server_id})
        context["assistant_list"] = self.get_assistant_list()
        return context


class DashboardView(TemplateView):
    template_name = 'bee_django_report/report/dashboard.html'

    # ===学生===
    def _get_students(self):
        try:
            if self.request.user.has_perm("bee_django_user.view_all_users"):
                queryset = User.objects.all().order_by('id')
            else:
                if self.request.user.has_perm("bee_django_user.view_teach_users"):
                    filter1 = Q(userprofile__user_class__assistant=self.request.user)
                else:
                    filter1 = Q(pk=None)
                if self.request.user.has_perm("bee_django_user.view_child_users"):
                    filter2 = Q(userprofile__parents=self.request.user.userprofile)
                else:
                    filter2 = Q(pk=None)
                queryset = User.objects.filter(filter1 | filter2).order_by('id').distinct()
            return queryset
        except:
            return User.objects.none()

    # ===班级===
    def _get_classes(self):
        try:
            from bee_django_user.models import UserClass
            if self.request.user.has_perm("bee_django_user.view_all_classes"):
                return UserClass.objects.filter(status=1)
            elif self.request.user.has_perm("bee_django_user.view_teach_classes"):
                return UserClass.objects.filter(assistant=self.request.user, status=1)
            else:
                return UserClass.objects.none()
        except:
            return []

    # ===录播===
    def _get_lives(self):
        try:
            from bee_django_course.models import UserLive
            if self.request.user.has_perm("bee_django_course.view_all_userlives"):
                q1 = Q(status=1)
            else:
                q1 = Q(pk=None)
            if self.request.user.has_perm("bee_django_course.view_teach_userlives"):
                users = get_teach_users(self.request.user)
                q2 = Q(user__in=users, status=1)
            else:
                q2 = Q(pk=None)

            if self.request.user.has_perm('bee_django_course.view_child_userlives'):
                users = self.request.user.get_child_users()
                q3 = Q(user__in=users, status=1)
            else:
                q3 = Q(pk=None)
            q = UserLive.objects.filter(q1 | q2 | q3).distinct()
            # 今日
            today_filter = UserLive.get_start_time_filter(scope='day', offset=0)
            today_user_lives = q.filter(today_filter)
            unview_today_user_lives = today_user_lives.filter(is_mentor_view=False)  # 今日未观看
            # 昨日
            yesterday_filter = UserLive.get_start_time_filter(scope='day', offset=-1)
            yesterday_user_live = q.filter(yesterday_filter)
            unview_yesterday_user_live = yesterday_user_live.filter(is_mentor_view=False)  # 昨日未观看
            return today_user_lives, unview_today_user_lives, yesterday_user_live, unview_yesterday_user_live
        except Exception as e:
            return [], [], [], []

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context["students"] = self._get_students()
        context["classes"] = self._get_classes()
        lives = self._get_lives()
        context["today_lives"] = lives[0]
        context["unview_today_lives"] = lives[1]
        context["yesterday_lives"] = lives[2]
        context["unview_yesterday_lives"] = lives[3]

        return context
