#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

import json, os, math, calendar, urllib, hashlib
from django.conf import settings
from utils import http_get, get_now, JSONResponse
from .models import Video
# moment.apis import get_user_moment_count
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpRequest
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile


# 创建工作室的分类
# 包括以名字命命的一级目录和两个二级目录
def create_studio_category(name):
    category_id = create_category(name)
    category_video_id = category_live_id = None
    if category_id:
        category_video_id = create_category(name + u"-课程", category_id)
        category_live_id = create_category(name + u"-直播", category_id)
    return category_id, category_live_id, category_video_id


# 修改工作室分类
def update_studio_category(category_id, name):
    update_category(category_id, name)
    return


# 创建分类
# super_categoryid为空，创建一级目录
def create_category(category_name, super_categoryid=None):
    # http://doc.bokecc.com/vod/dev/SparkAPI/spark10/
    if not hasattr(settings, "CC_CONFIG"):
        return
    url = "http://spark.bokecc.com/api/category/create"
    params_dict = {
        "userid": settings.CC_CONFIG.user_id,
        "name": category_name.encode('utf-8'),
        "format": "json"
    }
    if super_categoryid:
        params_dict["super_categoryid"] = super_categoryid

    qs = thqs(params_dict, 'video')
    url += "?" + qs
    res = http_get(url)
    res_json = str2json(res)
    if res_json:
        if res_json.has_key("category"):
            return res_json["category"]["id"]
    return None


# 编辑视频分类,重命名等
def update_category(category_id, category_name):
    # http://spark.bokecc.com/api/category/update
    # http://doc.bokecc.com/vod/dev/SparkAPI/spark10/
    if not hasattr(settings, "CC_CONFIG"):
        return
    url = "http://spark.bokecc.com/api/category/update"
    params_dict = {
        "categoryid": category_id,
        "userid": settings.CC_CONFIG.user_id,
        "name": category_name.encode('utf-8'),
        "format": "json"
    }

    qs = thqs(params_dict, 'video')
    url += "?" + qs
    http_get(url)
    return


# 创建直播间
def create_room(room_name):
    # http://doc.bokecc.com/live/dev/liveapi/#toc_11
    if not hasattr(settings, "CC_CONFIG"):
        return
    url = "http://api.csslcloud.net/api/room/create"
    params_dict = {
        "userid": settings.CC_CONFIG.user_id,
        "name": room_name.encode('utf-8'),
        "desc": room_name.encode('utf-8'),
        "templatetype": "1",
        "authtype": "2",
        "publisherpass": "111111",
        "assistantpass": "222222",
        "barrage": "0",
        "foreignpublish": "0"
    }
    qs = thqs(params_dict, 'live')
    url += "?" + qs
    try:
        res = http_get(url)
        res_json = str2json(res)
        if res_json:
            if res_json.has_key("result"):
                if res_json["result"] == 'OK':
                    return res_json["room"]["id"]
    except:
        return None
    return None


# 关闭直播间
def close_room(room_id):
    # https://doc.bokecc.com/live/live_http.html
    if not hasattr(settings, "CC_CONFIG"):
        return
    url = "http://api.csslcloud.net/api/room/close"
    params_dict = {
        "userid": settings.CC_CONFIG.user_id,
        "roomid": room_id

    }
    qs = thqs(params_dict, 'live')
    url += "?" + qs
    res = http_get(url)
    res_json = str2json(res)
    if res_json:
        if res_json.has_key("result"):
            return True
    return None

# 开启直播间
def open_room(room_id):
    if not hasattr(settings, "CC_CONFIG"):
        return
    url = "http://api.csslcloud.net/api/room/open"
    params_dict = {
        "userid": settings.CC_CONFIG.user_id,
        "roomid": room_id

    }
    qs = thqs(params_dict, 'live')
    url += "?" + qs
    res = http_get(url)
    res_json = str2json(res)
    if res_json:
        if res_json.has_key("result"):
            return True
    return None


# 获取直播间代码
def get_room_code(room_id):
    # http://doc.bokecc.com/live/dev/liveapi/#toc_22
    if not hasattr(settings, "CC_CONFIG"):
        return
    url = "http://api.csslcloud.net/api/room/code"
    params_dict = {
        "roomid": room_id,
        "userid": settings.CC_CONFIG.user_id
    }
    qs = thqs(params_dict, 'live')
    url += "?" + qs
    res = http_get(url)
    res_json = str2json(res)
    if res_json:
        if res_json.has_key("result"):
            if res_json["result"] == 'OK':
                return res_json
    return None



# 1.创建视频上传信息
def create_video_info(title, filename, filesize, categoryid=None):
    # http://doc.bokecc.com/vod/dev/uploadAPI/upload02/
    if not hasattr(settings, "CC_CONFIG"):
        return
    url = "http://spark.bokecc.com/api/video/create"
    if not categoryid:
        categoryid=settings.CC_CONFIG.category_id
    params_dict = {
        "userid": settings.CC_CONFIG.user_id,
        "title": title.encode('utf-8'),
        "description": filename.encode('utf-8'),
        "categoryid": categoryid,
        "filesize": filesize,
        "notify_url": settings.CC_CONFIG.video_callback_url.encode('utf-8'),
        "format": "json",

    }
    qs = thqs(params_dict, 'video')
    url += "?" + qs
    res = http_get(url)
    res_json = str2json(res)
    if res_json.has_key(u"uploadinfo"):
        return res_json
    return None


# 2 上传成功后记录用户video对应关系
def uplode_video_done(request):
    uid = request.POST.get("uid")
    title = request.POST.get("title")
    print('uplode_video_done', uid)
    if title:
        title = os.path.splitext(title)[0]
    videoid = request.POST.get("videoid")
    if videoid:
        ccvideo = Video()
        ccvideo.title = title
        ccvideo.created_by = request.user
        ccvideo.videoid = videoid
        ccvideo.save()
    res = {"error": 0}
    return JSONResponse(json.dumps(res, ensure_ascii=False))




# 获取直播回放记录
def get_live_watched():
    # http://doc.bokecc.com/live/dev/liveapi/#toc_26
    if not hasattr(settings, "CC_CONFIG"):
        return
    url = "http://api.csslcloud.net/api/statis/replay"
    now = get_now()
    params_dict = {
        "userid": settings.CC_CONFIG.user_id,
        "starttime": "2017-07-27 15:00",
        "endtime": "2017-07-27 19:00",
        "pageindex": "1",
        "pagenum": "50",

    }
    qs = thqs(params_dict, 'live')
    url += "?" + qs
    res = http_get(url)
    print(res)
    res_json = str2json(res)
    print(res_json)


# 未使用
# 获取视频播放代码
def get_video_play_code(videoid):
    # http://doc.bokecc.com/vod/dev/SparkAPI/spark06/
    if not hasattr(settings, "CC_CONFIG"):
        return
    url = "http://spark.bokecc.com/api/video/playcode"
    params_dict = {
        "videoid": videoid,
        "userid": settings.CC_CONFIG.user_id,
        "player_width": "100%",
        "player_height": "40%",
        "auto_play": "true",
        "format": "json",

    }
    qs = thqs(params_dict, 'live')
    url += "?" + qs
    # print(url)
    res = http_get(url)
    # print(res)
    res_json = str2json(res)
    # print(res_json)
    return


# 获取点播视频播放地址
def get_video_str(video_id):
    if not hasattr(settings, "CC_CONFIG"):
        return
    src = "https://p.bokecc.com/playhtml.bo?vid=" + video_id + "&siteid=" + settings.CC_CONFIG.user_id + "&autoStart=false&playerid=" + settings.CC_CONFIG.player_id + "&playertype=1"
    return src

# 获取录播视频地址
def get_live_str(video_id):
    if not hasattr(settings, "CC_CONFIG"):
        return
    url="http://p.bokecc.com/api/mobile"
    params_dict = {
        "videoid": video_id,
        "userid": settings.CC_CONFIG.user_id,
        "format": "json",
    }
    qs = thqs(params_dict, 'video')
    url += "?" + qs
    res = http_get(url)
    res_json = str2json(res)
    if res_json.has_key("error"):
        return None
    return res_json["video"]["copy"][0]["playurl"]


# 删除视频
def delete_video(vodio_id):
    # http://doc.bokecc.com/vod/dev/SparkAPI/spark08/
    if not hasattr(settings, "CC_CONFIG"):
        return
    url = "http://spark.bokecc.com/api/video/delete"
    params_dict = {
        "userid": settings.CC_CONFIG.user_id,
        "videoid": vodio_id,
        "format": "json",

    }
    qs = thqs(params_dict, 'video')
    url += "?" + qs
    res = http_get(url)
    res_json = str2json(res)
    if res_json.has_key(u"result"):
        if res_json["result"] == 'OK':
            return True
    return



# 获取某条视频某日的观看记录
# def get_video_play_logs(video_id, date):
#     # https://doc.bokecc.com/index.php?c=content&a=list&catid=295
#     url = "http://spark.bokecc.com/api/playlog/video/v2"
#     params_dict = {
#         "userid": settings.COURSE_CC_USERID,
#         "videoid": video_id,
#         "date": date,
#         "num_per_page": 5000,
#         "page": 1
#     }
#     qs = thqs(params_dict, 'video')
#     url += "?" + qs
#     res = http_get(url)
#     res_json = str2json(res)
#     if res_json.has_key(u"total") and res_json.has_key(u"play_log"):
#         return res_json["total"], res_json["play_log"]
#     return None, None


# 获取日期内全部视频的观看记录
# def get_play_logs(date):
#     # https://doc.bokecc.com/index.php?c=content&a=list&catid=315
#     url = "http://spark.bokecc.com/api/playlog/user/v2"
#     params_dict = {
#         "userid": settings.COURSE_CC_USERID,
#         "date": date,
#         "num_per_page": 5000,
#         "page": 1
#     }
#     qs = thqs(params_dict, 'video')
#     url += "?" + qs
#     res = http_get(url)
#     res_json = str2json(res)
#     if res_json.has_key(u"total") and res_json.has_key(u"play_log"):
#         return res_json["total"], res_json["play_log"]
#     return None, None


# =================

def get_timestamp(_datetime):
    timestamp = calendar.timegm(_datetime.utctimetuple())
    return timestamp



def thqs(params, type_str):
    # http://doc.bokecc.com/live/dev/liveapi/#toc_39
    if not hasattr(settings, "CC_CONFIG"):
        return
    qs = ""
    if type_str == 'live':
        salt = settings.CC_CONFIG.live_apikey
    else:
        salt = settings.CC_CONFIG.video_apikey

    if params and len(params) > 0:
        sortd_params = sorted(params.iteritems(), key=lambda item: item[0])
        qs = urllib.urlencode(sortd_params)

    timestamp = get_timestamp(get_now())

    qf = qs
    if len(qf) > 0:
        qf = "%s&" % qf
    qf = "%stime=%d&salt=%s" % (qf, timestamp, salt)

    qmd5 = hashlib.md5(qf).hexdigest()
    hqs = qs
    if len(hqs) > 0:
        hqs = "%s&" % hqs
    hqs = "%stime=%d&hash=%s" % (hqs, timestamp, qmd5)

    return hqs



# 结果转json
def str2json(res):
    try:
        res_json = json.loads(res)
    except:
        res_json = None
    return res_json
