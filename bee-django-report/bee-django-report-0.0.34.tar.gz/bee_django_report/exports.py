#!/usr/bin/env python
# -*- coding:utf-8 -*-


__author__ = 'bee'
from django.contrib.auth import get_user_model

from .utils import save_week_report
from .dt import get_year_month_week, get_datetime_with_scope_offset
from .models import ClassWeek

User = get_user_model()


def filter_local_datetime(_datetime):
    return _datetime


class ClassWeekReport():
    start_dt = None
    end_dt = None
    year = None
    month = None
    week = None
    offset = None

    def auto_save_db(self, class_id=None, offset=-1):
        self.offset = offset
        self.start_dt, self.end_dt = get_datetime_with_scope_offset(scope='week', offset=self.offset)
        self.year, self.month, self.week = get_year_month_week(self.start_dt)
        if class_id:
            classes = [self._get_class(class_id)]
        else:
            classes = self._get_classes()
        for c in classes:
            if not c:
                return
            ret = self._check_class(c.id)
            # 检查是否已经保存
            if not ret:
                continue
            users = self._get_users(c)
            mentor = self._get_mentor(c)
            if users:
                for user in users:
                    self.save_report(c=c, type_str='student', user=user, mentor=mentor)
            if mentor:
                self.save_report(c=c, type_str='mentor', user=None, mentor=mentor)

    def _check_class(self, class_id):
        report_list = ClassWeek.objects.filter(year=self.year, week=self.week, class_id=class_id)
        if report_list.exists():
            return False
        return True

    def _get_classes(self):
        try:
            from bee_django_user.models import UserClass
            pass
        except:
            return []
        return UserClass.objects.all()

    def _get_class(self, class_id):
        try:
            from bee_django_user.models import UserClass
            return UserClass.objects.get(id=class_id)
        except:
            return None

    # 获取一个班的所有学生
    def _get_users(self, user_class):
        try:
            return User.objects.filter(userprofile__user_class=user_class)
        except Exception as e:
            print(e)
            return []

    # 获取一个班的助教，返回setting.auth_user
    def _get_mentor(self, user_class):
        return user_class.assistant

    # 获取用户的练习时长，返回：分钟数
    def _get_user_live_mins_count_days(self, user):
        try:
            from bee_django_course.exports import get_user_live_mins_count_days
            mins, count, days = get_user_live_mins_count_days(user, self.start_dt, self.end_dt)
            return mins, count, days
        except:
            return 0, 0, 0

    # 获取用户的发日志数，返回：条数
    def _get_user_feed_count(self, user):
        try:
            from bee_django_social_feed.exports import get_user_feed_count
            return get_user_feed_count(user, self.start_dt, self.end_dt)
        except:
            return 0

    # 获取用户最后一个学习的课件，返回：user_course_section的id
    def _get_user_last_user_section_id(self, user):
        try:
            from bee_django_course.exports import get_user_last_course_section
            user_course_section = get_user_last_course_section(user=user, start_dt=None, end_dt=self.end_dt)
            if user_course_section:
                return user_course_section.id
            else:
                return None
        except:
            return None

    # 获取用户录播被助教观看次数
    def _get_mentor_view_count(self, user):
        try:
            from bee_django_course.models import UserLive
            mins, count, mentor_view_count = UserLive.get_user_live_detail([user], scope="week", offset=self.offset)
            return mins, count, mentor_view_count
        except:
            return 0

    def _get_mentor_comment_count(self, user):
        try:
            from bee_django_course.models import UserLive
            count = UserLive.get_mentor_comment_count(user, self.start_dt, self.end_dt)
            return count
        except:
            return 0

    def save_report(self, c, type_str, user, mentor):
        type_int = 0
        if type_str == 'student':
            type_int = 3
        elif type_str == 'mentor':
            type_int = 9
        if user:
            _user = user
        else:
            _user = mentor
        live_mins, live_count, live_days = self._get_user_live_mins_count_days(_user)
        live_mins, live_count, live_watched_count = self._get_mentor_view_count(_user)
        live_commented_count = self._get_mentor_comment_count(_user)
        save_week_report(class_id=c.id, year=self.year, week=self.week, type_int=type_int, start_date=self.start_dt,
                         end_date=self.end_dt, user=user, mentor=mentor,
                         live_mins=live_mins,
                         feed_count=self._get_user_feed_count(_user),
                         live_days=live_days,
                         live_count=live_count,
                         live_watched_count=live_watched_count,
                         live_commented_count=live_commented_count,
                         last_user_section_id=self._get_user_last_user_section_id(_user))


def get_class_name(class_id):
    try:
        from bee_django_user.models import UserClass
        c = UserClass.objects.get(id=class_id)
        return c.name
    except:
        return class_id


def get_section_name(user_course_section_id):
    try:
        from bee_django_course.models import UserCourseSection
        ucs = UserCourseSection.objects.get(id=user_course_section_id)
        # print(ucs.section.name)
        return ucs.section.name
    except:
        return ""
