# -*- coding: utf-8 -*-
__author__ = 'bee'

import urllib, urllib2, pytz, json, random, datetime
from django.http import HttpResponse
from django.db.models import Count, Sum, Max, Min
from django.db.models.functions import TruncMonth, TruncDay
from django.utils import timezone
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .models import UserLive, User, UserCourseSection
from bee_django_course import signals
from .dt import LOCAL_TIMEZONE


# =====http====
def http_get(url):
    f = urllib.urlopen(url)
    s = f.read()
    return s


def http_post(url, parameters=None):
    parameters = urllib.urlencode(parameters)
    request = urllib2.Request(url, parameters)
    request.add_header('Content-Type', 'application/x-www-form-urlencoded')
    res_data = urllib2.urlopen(request, timeout=10)
    res = res_data.read()
    return res


# ====dt====
# 获取本地当前时间
def get_now(tz=LOCAL_TIMEZONE):
    return timezone.now()


class JSONResponse(HttpResponse):
    def __init__(self, obj):
        if isinstance(obj, dict):
            _json_str = json.dumps(obj)
        else:
            _json_str = obj
        super(JSONResponse, self).__init__(_json_str, content_type="application/json;charset=utf-8")


def page_it(request, query_set, url_param_name='page', items_per_page=25):
    paginator = Paginator(query_set, items_per_page)

    page = request.GET.get(url_param_name)
    try:
        rs = paginator.page(page)
    except PageNotAnInteger:
        rs = paginator.page(1)
    except EmptyPage:
        rs = paginator.page(paginator.num_pages)

    return rs


# 获取用户姓名
def get_user_name(user):
    try:
        user_name = getattr(user, settings.USER_NAME_FIELD)
    except:
        user_name = user.username
    return user_name


# 返回直播分钟数，直播次数，直播天数
def get_user_live_data(user, start_dt=None, end_dt=None):
    vod_list = UserLive.objects.filter(status__in=[1, 2]).filter(user=user).filter(record_status=10)
    if start_dt:
        vod_list = vod_list.filter(start_time__gte=start_dt)
    if end_dt:
        vod_list = vod_list.filter(start_time__lt=end_dt)
    if vod_list.count() == 0:
        return 0, 0, 0
    res_mins = vod_list.aggregate(
        sum_duration=Sum('duration'))
    days_qurey_set = vod_list.annotate(day=TruncDay('start_time', tzinfo=LOCAL_TIMEZONE)).values('day') \
        .annotate(count=Count('id'), total=Sum('duration')).values('day', 'count', 'total') \
        .order_by('day')
    days_count = days_qurey_set.count()
    return res_mins["sum_duration"] / 60, vod_list.count(), days_count


# 某人是否可以观看视频，观看视频后是否能被记录为【助教已观看】。
# 条件1：有权限，条件2：录制本人，条件3：超过48小时。
def can_view_expired_live(user, user_live):
    # 本人可看，但不记入观看
    if user == user_live.user:
        return True, False

    # 判断是否助教
    is_mentor = user.is_user_assistant(user_live.user)

    # 设置过期时间
    if hasattr(settings, "COURSE_LIVE_EXPIRED_HOURS"):
        expired_dt = user_live.start_time + datetime.timedelta(hours=settings.COURSE_LIVE_EXPIRED_HOURS)
        # 未过期
        if timezone.now() < expired_dt:
            if is_mentor:
                return True, True
            else:
                return True, False
        # 已过期
        else:
            if user.has_perm('bee_django_course.view_expired_userlives'):
                return True, False
            else:
                return False, False
    # 未设置过期时间
    else:
        if is_mentor:
            return True, True
        else:
            return True, False


# from .views import live_finish

from gensee import vod_sync


def gensee_vod_sync(day=0):
    page = 1
    totalPages = 1
    sync_count = 0
    while page <= totalPages:
        vod_list_res = vod_sync(page=page, day=day)
        try:
            if not vod_list_res["code"] == "0":
                return
        except:
            return
        totalPages = vod_list_res["page"]["totalPages"]
        vod_list = vod_list_res["list"]
        page += 1
        for i, v in enumerate(vod_list):
            user_live = save_gensee_live(v)
            if user_live:
                live_finish(user_live)
                sync_count += 1
    return sync_count


def save_gensee_live(vod):
    live_id = vod["id"]  # 点播ID
    room_id = vod["webcastId"]  # 直播ID
    res = UserLive.objects.filter(live_id=live_id)
    # 重复
    if res.exists():
        return False
    # 不是学生录播
    if not vod["creator"] == 30196111:
        return False
    # 找不到对应学生
    try:
        user = User.objects.get(userprofile__gensee_room_id=room_id)
    except:
        return False
    try:
        user_live = UserLive()
        user_live.provider_name = 'gensee'
        user_live.room_id = room_id  # 直播ID
        user_live.live_id = live_id  # 点播ID
        user_live.stop_status = 10
        user_live.record_status = 10
        start_time = LOCAL_TIMEZONE.localize(datetime.datetime.fromtimestamp(int(vod["recordStartTime"] / 1000)))
        end_time = LOCAL_TIMEZONE.localize(datetime.datetime.fromtimestamp(int(vod["recordEndTime"] / 1000)))
        user_live.record_video_id = vod["recordId"]  # 该点播使用的录制件ID
        user_live.replay_url = vod["attendeeJoinUrl"]  # 加入URL
        user_live.start_time = start_time  # 录制开始时间
        user_live.end_time = end_time  # 录制结束时间
        user_live.duration = int(vod["duration"] / 1000)  # 内容时长。单位是毫秒。
        user_live.user = user
        user_live.save()
        return user_live
    except Exception as e:
        print (e)
        return False


def update_live_mins(user):
    live_set = user.userlive_set.filter(record_status='10', status__in=[1, 2])
    total_mins = 0
    for e in live_set:
        if e.duration > 60:
            min = e.duration / 60
            total_mins += min
    if hasattr(user, 'set_live_mins'):
        user.set_live_mins(total_mins)


# 直播转码完成后的一系列操作：更新课件进度，发送信号
def live_finish(userlive, timedelta=None):
    if not timedelta:
        timedelta = userlive.duration
    if timedelta < 60:
        return

    if not userlive.user:
        return

    # 更新课件学习时间
    user_course_section = UserCourseSection.get_user_last_course_section(userlive.user)
    if user_course_section:
        user_course_section.update_work_time(timedelta / 60)
        signals.ucs_update_time.send(sender=UserCourseSection, ucs=user_course_section)
        update_live_mins(userlive.user)

    coin_multiple = save_coin_multiple(userlive)
    signals.live_callback_finished.send(sender=UserLive, user_live=userlive, coin_multiple=coin_multiple)
    return


def save_coin_multiple(userlive):
    coin_multiple = 1
    r = random.randint(1, 1000)
    if r >= 980:
        coin_multiple = 3
    elif r >= 900:
        coin_multiple = 2
    userlive.coin_multiple = coin_multiple
    userlive.save()
    return coin_multiple
