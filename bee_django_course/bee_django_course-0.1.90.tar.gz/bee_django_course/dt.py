#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

import pytz, calendar, time,datetime
from calendar import monthrange
from django.utils import timezone

LOCAL_TIMEZONE = pytz.timezone('Asia/Shanghai')


def get_now(tz=LOCAL_TIMEZONE):
    now = timezone.now()
    return now


# 获取今日0点时间，默认返回北京时间
def get_today(tz=LOCAL_TIMEZONE):
    now = timezone.now()
    year = now.strftime("%Y")
    month = now.strftime("%m")
    day = now.strftime("%d")
    today = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=0, minute=0, second=0,
                                 tzinfo=tz)
    return today


# 获取当周周日晚23点23分23秒
def get_current_week_range_datetime():
    today = get_today()
    start_date = today - datetime.timedelta(days=today.weekday())
    end_date = start_date + datetime.timedelta(days=7)
    end_date = end_date - datetime.timedelta(seconds=1)
    # print(start_date,end_date, '1')
    return start_date, end_date


def add_months(dt, months):
    month = dt.month - 1 + months
    year = dt.year + month / 12
    month = month % 12 + 1
    day = min(dt.day, monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def add_weeks(weeks):
    today = get_today()
    days = today.weekday()   # 0到6代表周一到到周日
    start_dt = today + datetime.timedelta(days=-days + weeks * 7)
    end_dt = start_dt + datetime.timedelta(7)
    return start_dt, end_dt



# 获取第几周或几月
def get_year_month_week(_datetime):
    year = _datetime.strftime("%Y")
    month = _datetime.strftime("%m")
    week = _datetime.strftime("%W")
    return year, month, week


# 获取开始时间和结束时间
# scope：范围：day/month/week
# offset: 偏移时间，正为延后，负为以前
def get_datetime_with_scope_offset(scope, offset):
    offset=int(offset)
    today = get_today()
    start_time = None
    end_time = None
    if scope == 'day':
        days = offset
        start_time = (today + datetime.timedelta(days=days))
        end_time = (start_time + datetime.timedelta(days=1))
    elif scope == 'month':
        first_day = (today + datetime.timedelta(days=-today.day + 1))
        start_time = add_months(first_day, offset)
        end_time = add_months(first_day, offset + 1)
    elif scope == 'week':
        start_time, end_time = add_weeks(offset)
    return start_time, end_time