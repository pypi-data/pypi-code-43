# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.
# 周报
class ClassWeek(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='classWeek_student', verbose_name='学生', null=True)
    class_id = models.IntegerField("班级id", null=True)
    year = models.IntegerField()  # 年
    week = models.IntegerField(null=True)  # 第几周
    type_int = models.IntegerField(default=0)  # 1-班级总数记录 2-平均数记录 3-班级学生的记录 -9:班级老师的记录
    start_date = models.DateField()  # 开始日期
    end_date = models.DateField()
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='classWeek_mentor', null=True,
                               on_delete=models.SET_NULL)  # 助教
    feed_count = models.IntegerField(default=0)  # 发表日志数
    live_mins = models.IntegerField(default=0)  # 练习时长
    live_days = models.IntegerField(default=0)  # 练习天数
    live_count = models.IntegerField(default=0)  # 练习次数
    live_watched_count = models.IntegerField(default=0)  # 被助教观看的次数
    live_watched_days = models.IntegerField(default=0)  # 被助教观看的天数
    live_commented_count = models.IntegerField(default=0)  # 被助教评论的次数
    last_user_section_id = models.IntegerField(null=True)  # 最后一个学习的课件
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = 'bee_django_report_class_week'
        app_label = 'bee_django_report'
        ordering = ['created_at']
        # permissions = (
        #     ('can_view_mission', '可以进入mission管理页'),
        # )

    def __str__(self):
        return self.id.__str__()

    def __unicode__(self):
        return self.id.__str__()


# 报表 助教周分数报表
class MentorScoreWeek(models.Model):
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    year = models.IntegerField(verbose_name='年')  # 年
    week = models.IntegerField(null=True, verbose_name='第几周')  # 第几周
    score = models.FloatField(null=True, verbose_name='分数')  # 分数
    rank = models.IntegerField(null=True)  # 排名
    level = models.IntegerField(null=True)  # 等级，1优10中20差
    info = models.TextField(null=True, verbose_name='备注', blank=True)  # 备注
    created_at = models.DateTimeField(auto_now_add=True)  # 添加时间

    class Meta:
        db_table = 'bee_django_report_montor_score_week'
        app_label = 'bee_django_report'
        ordering = ['created_at']
        permissions = (
            ('view_mentorscoreweek', '可以查看全部助教分数'),
        )

    def __unicode__(self):
        return (
                "mentorScore->week:" + self.week.__str__() + ",mentor:" + self.mentor.__str__() + ",score:" + self.score.__str__())

    def __str__(self):
        return (
                "mentorScore->week:" + self.week.__str__() + ",mentor:" + self.mentor.__str__() + ",score:" + self.score.__str__())

    @classmethod
    def update_rank(cls, year, week):
        level = [0.2, 0.7, 0.1]
        reports = cls.objects.filter(year=year, week=week).order_by('-score')
        count = reports.count()
        score_last = None
        rank_last = 1

        # 排名
        for i, r in enumerate(reports):
            score = r.score
            if not score_last == score:
                rank_last = i + 1
            r.rank = rank_last
            r.save()
            score_last = score

        # 分数级别
        if count > 0:

            # 第一级
            level1_count = int(level[0] * count) + 1
            reports_temp = reports[:level1_count]
            level1_score = reports_temp[:level1_count][-1].score  # 最低分
            level1_reports = reports.filter(score__gte=level1_score)
            for r in level1_reports:
                r.level = 1
                r.save()

            # 第三级
            level3_count = int(level[2] * count) + 1
            reports_temp = reports[::-1]
            level3_score = reports_temp[:level3_count][-1].score  # 最高分
            level3_reports = reports.filter(score__lte=level3_score)
            for r in level3_reports:
                r.level = 3
                r.save()

            # 第二级
            level2_reports = reports.filter(score__lt=level1_score, score__gt=level3_score)
            for r in level2_reports:
                r.level = 2
                r.save()

        return True


# 每次保存分数时，更新排名
# @receiver(post_save, sender=MentorScoreWeek)
# def update_menter_rank_week(sender, **kwargs):
#     menter_score = kwargs['instance']
# print(sender)

#     year = menter_score.year
#     week = menter_score.week
#     MentorScoreWeek.update_rank(year, week)
#     return
class Report(models.Model):
    class Meta:
        db_table = 'bee_django_report'
        app_label = 'bee_django_report'
        permissions = (
            ('can_view_report', '可以查看报表'),
        )

    # ======用户部分=========
    # 获取全部客服
    @classmethod
    def get_server_list(cls):
        try:
            from bee_django_user.models import UserProfile
            return User.objects.filter(groups__name__in=UserProfile.get_agent_groupname_list())
        except:
            return User.objects.none()

    # 获取全部助教
    @classmethod
    def get_assistant_list(cls,user):
        try:
            from bee_django_user.models import UserProfile
            user_collection = user.get_student_list()
            return user_collection.filter(groups__name__in=UserProfile.get_assistant_groupname_list())
        except:
            return User.objects.none()

    # 获取全部班级
    @classmethod
    def get_class_list(cls,user):
        try:
            class_collection = user.userprofile.get_class_list()
            return class_collection
        except:
            return None

    # ======课程部分=========
    # 获取学生最近一个的user_course_section
    @classmethod
    def get_user_current_course_section(cls, user):
        try:
            from bee_django_course.models import UserCourseSection
            ucs = UserCourseSection.get_user_last_course_section(user)
            return ucs
        except:
            return None

    # 获取学生课程的通过的section
    @classmethod
    def get_user_pass_section_list(cls, user_course):
        try:
            from bee_django_course.models import UserCourseSection
            return UserCourseSection.get_user_pass_sections(user_course)
        except:
            return None
