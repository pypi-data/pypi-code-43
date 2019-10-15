#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'
import json, datetime
from django.utils import timezone
from django.conf import settings
from utils import http_post
from dt import get_now, get_datetime_with_scope_offset, LOCAL_TIMEZONE


# 获取直播间id
def create_room(room_name):
    if not hasattr(settings, "GENSEE_CONFIG"):
        return
    create_webcast_parameters = {
        "subject": room_name.encode('utf-8'),
        "startTime": timezone.now(),
        "organizerToken": settings.GENSEE_CONFIG.student_organizerToken,
        "panelistToken": settings.GENSEE_CONFIG.student_panelistToken,
        "attendeeToken": "",
        "loginName": settings.GENSEE_CONFIG.gensee_manke_account.username,
        "password": settings.GENSEE_CONFIG.gensee_manke_account.password
    }
    create_webcast_res = gensee_api_post("/webcast/created", create_webcast_parameters)
    if create_webcast_res and create_webcast_res["code"] == "0":
        return create_webcast_res["id"]
    else:
        return None


# 删除直播间
def delete_room(room_id):
    if not hasattr(settings, "GENSEE_CONFIG"):
        return
    delete_webcast_parameters = {
        "webcastId": room_id,
        "loginName": settings.GENSEE_CONFIG.gensee_manke_account.username,
        "password": settings.GENSEE_CONFIG.gensee_manke_account.password
    }
    create_webcast_res = gensee_api_post("/webcast/deleted", delete_webcast_parameters)
    if create_webcast_res and create_webcast_res["code"] == "0":
        return True
    else:
        return False


# 获取直播间信息
def get_room_info(room_id):
    if not hasattr(settings, "GENSEE_CONFIG"):
        return
    live_webcast_res = gensee_api_post("/webcast/setting/info",
                                       {"webcastId": room_id, "loginName":
                                           settings.GENSEE_CONFIG.gensee_manke_account.username,
                                        "password": settings.GENSEE_CONFIG.gensee_manke_account.password})
    if live_webcast_res["code"] == "0":
        room = live_webcast_res
    else:
        room = None
    return room


def gensee_api_post(url, parameters):
    if not hasattr(settings, "GENSEE_CONFIG"):
        return
    url = settings.GENSEE_CONFIG.genseeUrl + url
    res = http_post(url, parameters)
    try:
        j = json.loads(res)
    except Exception as e:
        print(e)
        j = None
    return j


# 同步gensee的录播记录  /webcast/vod/sync
# 分页获取本站点中已发布的点播数据。每页最大返回 50 条数据
# 该 API 要求认证用户具有管理员角色。
def vod_sync(page=1, day=0):
    if not hasattr(settings, "GENSEE_CONFIG"):
        return
    now = get_now()
    # 取前一天数据
    if day == -1:
        start_dt, end_dt = get_datetime_with_scope_offset("day", -1)

        # yesterday = now - datetime.timedelta(days=1)
        # y_year = yesterday.strftime("%Y")
        # y_month = yesterday.strftime("%m")
        # y_day = yesterday.strftime("%d")
        # # t_year = now.strftime("%Y")
        # # t_month = now.strftime("%m")
        # # t_day = now.strftime("%d")
        # start_time_str = y_year + '-' + y_month + "-" + y_day + " 00:00:00"
        # end_time_str = y_year + '-' + y_month + "-" + y_day + " 23:59:59"
        # startTime = datetime.datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        # endTime = datetime.datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

    # 取前31分钟数据
    else:
        start_dt = now - datetime.timedelta(minutes=31)
        end_dt = now
    start_dt = start_dt.astimezone(tz=LOCAL_TIMEZONE)
    end_dt = end_dt.astimezone(tz=LOCAL_TIMEZONE)
    vod_list_res = gensee_api_post("/webcast/vod/sync",
                                   {"loginName": "admin@zenweiqi.com", "password": "888888", "pageNo": page,
                                    "startTime": start_dt, "endTime": end_dt})
    return vod_list_res
    # try:
    #     if vod_list_res["code"] == "0":
    #         totalPages = vod_list_res["page"]["totalPages"]
    #         page += 1
    #     else:
    #         break
    # except:
    #     break
    # while page <= totalPages:
