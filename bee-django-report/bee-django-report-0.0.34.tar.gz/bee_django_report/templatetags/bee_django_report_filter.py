#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from datetime import datetime
from django import template
from django.conf import settings
from django.contrib.auth import get_user_model

from bee_django_report.models import Report
from bee_django_report.utils import get_user_name
from bee_django_report.exports import get_class_name as exports_get_class_name
from bee_django_report.exports import get_section_name as exports_get_section_name
from bee_django_report.exports import filter_local_datetime

register = template.Library()
User = get_user_model()


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)


#
# # 本地化时间
@register.filter
def local_datetime(_datetime):
    return filter_local_datetime(_datetime)


# 获取学生姓名，及详情链接
@register.filter
def get_name_detail(user, show_detail=True):
    user_name = get_user_name(user)
    if not show_detail:
        return user_name
    if settings.USER_DETAIL_EX_LINK:
        link = "<a href='" + settings.USER_DETAIL_EX_LINK + user.id.__str__() + "/'>" + user_name + "</a>"
    else:
        link = user_name
    return link


# 获取学生姓名，及列表链接
@register.filter
def get_name_list_search(user,user_search_field):
    user_search_field = user_search_field.__str__()
    user_name = get_user_name(user)
    if settings.USER_LIST_EX_LINK:
        link = "<a href='" + settings.USER_LIST_EX_LINK + user_search_field + "'>" + user_name + "</a>"
    else:
        link = user_name
    return link


# 获取学生
@register.filter
def get_user(user_id):
    try:
        user = User.objects.get(id=user_id)
        return user
    except:
        return None


# 获取班级名称
@register.filter
def get_class_name(class_id):
    return exports_get_class_name(class_id)


# 获取课件名称
@register.filter
def get_section_name(user_course_section_id):
    return exports_get_section_name(user_course_section_id)

# 获取学生的最近一个的user_course_section
@register.simple_tag
def get_user_current_course_section(user):
    user_course_section=Report.get_user_current_course_section(user)
    return user_course_section
#
# # 获取学生的最近一个的user_course_section
# @register.simple_tag
# def get_user_current_course(user):
#     user_course_section = Report.get_user_current_course(user)
#     return user_course_section

# 获取user_course的通过的所有section
@register.filter
def get_user_pass_section_count(user_course):
    return Report.get_user_pass_section_list(user_course).count()

