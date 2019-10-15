#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'zhangyue'

from datetime import datetime
from django import template

from django.contrib.auth.models import User, Group, Permission
from bee_django_user.exports import get_user_leave_status

register = template.Library()


# 求两个值的差的绝对值
@register.filter
def get_difference_abs(a, b):
    return abs(a - b)


# 组是否有权限
@register.filter
def has_permission(group, permission_name):
    try:
        if group.permissions.get(codename=permission_name):
            return True
        return False
    except:
        return False


# 组是否有权限
@register.filter
def has_manage(user):
    try:
        if user.userprofile.has_group("管理员") or user.userprofile.has_group("客服") or user.userprofile.has_group("助教"):
            return True

    except:
        return False
    return False


# 本地化时间
# @register.filter
# def local_datetime(_datetime):
#     return filter_local_datetime(_datetime)

# 获取学生的请假状态
@register.simple_tag
def get_leave_status(user):
    status = get_user_leave_status(user)
    if status:
        return "请假中"
    return


# 获取【本周】学生练习的分钟数，次数，助教观看次数
@register.simple_tag
def get_user_live_detail(user, time):
    try:
        from bee_django_course.models import UserLive
        if time == u'本日':
            scope = 'day'
            offset = 0
        elif time == u'昨日':
            scope = 'day'
            offset = -1
        elif time == u'本周':
            scope = 'week'
            offset = 0
        elif time == u'上周':
            scope = 'week'
            offset = -1
        elif time == u'本月':
            scope = 'month'
            offset = 0
        elif time == u'上月':
            scope = 'month'
            offset = -1
        else:
            return 0, 0, 0
        return UserLive.get_user_live_detail([user], scope=scope, offset=offset)
    except Exception as e:
        return 0, 0, 0


# 获取班级剩余m币
@register.filter
def get_class_coin(class_id):
    try:
        from bee_django_coin.models import OtherCoinCount
        record = OtherCoinCount.objects.get(coin_type__identity='user_class', coin_content_id=class_id)
        return record.count
    except:
        return None
