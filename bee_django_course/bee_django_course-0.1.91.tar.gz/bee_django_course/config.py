#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'


from django.conf import settings

class Gensee():

    genseeUrl = "http://zenweiqi.gensee.com/integration/site"
    student_password = "manxuetang!"
    student_organizerToken = '111111'
    student_panelistToken = '222222'

    class gensee_admin_account:
        username = "admin@zenweiqi.com"
        password = "888888"


    class gensee_manke_account:
        username = "manke@zhenpuedu.com"
        password = "manxuetang123"


    class gensee_stage_account:
        username = "stage@zenweiqi.com"
        password = '111111'

class CC():
    user_id = '116A0DDBD5490C3E'
    live_apikey = "xJSsamNrYlfun55MksEMHcHM9DG6xdyt"
    video_apikey = "lL9ZS4sRgi7GoHW5BFukFk7ZInQOgW86"
    player_id = '73713B694B1A64E3'
    category_id = '3782E07C245BB580'
    video_callback_url = ''

class Qiniu():
    ak='w4yaDe9SPuChxJHBQnefqlond1704XS4vHU_3sMK'
    sk='stoLiR-4tCV7v0A51S-ly4fFJgNWI_b0USdQccua'
    bucket_name='xinanxiangju-video'
    domain='video.xinanxiangju.com'

class Tencent():
    live_key="8ea93cf8031d0802fbcb30bf406b0624"



# ======初始化========
# cc
if "cc" in settings.COURSE_LIVE_PROVIDER_LIST or "cc" == settings.COURSE_VIDEO_PROVIDER_NAME:
    settings.CC_CONFIG=CC()
#
# qiniu
if "qiniu" == settings.COURSE_VIDEO_PROVIDER_NAME:
    settings.QINIU_CONFIG=Qiniu()
#
# gensee
if "gensee" in settings.COURSE_LIVE_PROVIDER_LIST:
    settings.GENSEE_CONFIG=Gensee()

if "tencent" in settings.COURSE_LIVE_PROVIDER_LIST:
    settings.TENCENT_CONFIG=Tencent()
    pass
