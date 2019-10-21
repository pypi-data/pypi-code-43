#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'


from django.conf import settings

class Gensee():
    pass

class CC():
    pass

class Qiniu():
    ak='w4yaDe9SPuChxJHBQnefqlond1704XS4vHU_3sMK'
    sk='stoLiR-4tCV7v0A51S-ly4fFJgNWI_b0USdQccua'
    bucket_name='xinanxiangju-video'
    domain='video.xinanxiangju.com'

class Tencent():
    pass



# ======初始化========
# cc
if "cc" in settings.COURSE_LIVE_PROVIDER_LIST or "cc" == settings.COURSE_VIDEO_PROVIDER_NAME:
    settings.CC_CONFIG=CC()
#
# qiniu
if "qiniu" == settings.COURSE_VIDEO_PROVIDER_NAME:
    settings.CC_CONFIG=Qiniu()
#
# gensee
if "gensee" in settings.COURSE_LIVE_PROVIDER_LIST:
    settings.GENSEE_CONFIG=Gensee()

if "tencent" in settings.COURSE_LIVE_PROVIDER_LIST:
    settings.TENCENT_CONFIG=Tencent()
    pass
