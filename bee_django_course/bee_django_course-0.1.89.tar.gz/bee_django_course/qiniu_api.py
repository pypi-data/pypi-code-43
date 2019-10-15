# -*- coding: utf-8 -*-
__author__ = 'bee'
from django.conf import settings

from qiniu import Auth
from qiniu import BucketManager

# 上传视频到七牛，需要先获取的token
def get_qiniu_token(key):
    if not hasattr(settings, "QINIU_CONFIG"):
        return
    access_key = settings.QINIU_CONFIG.ak
    secret_key = settings.QINIU_CONFIG.sk
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = settings.QINIU_CONFIG.bucket_name
    # key 上传后保存的文件名

    # 生成上传 Token，可以指定过期时间等
    # 上传策略示例
    # https://developer.qiniu.com/kodo/manual/1206/put-policy
    policy = {
        # 'callbackUrl':'https://requestb.in/1c7q2d31',
        # 'callbackBody':'filename=$(fname)&filesize=$(fsize)'
        # 'persistentOps':'imageView2/1/w/200/h/200'
    }
    # 3600为token过期时间，秒为单位。3600等于一小时
    token = q.upload_token(bucket_name, key=key.encode('utf-8'), expires=3600, policy=policy)
    return token


def get_video_str(file_name):
    if not hasattr(settings, "QINIU_CONFIG"):
        return ''
    if file_name:
        return "http://" + settings.QINIU_CONFIG.domain + "/" + file_name
    else:
        return ""