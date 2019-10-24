# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import requests, json
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from dss.Serializer import serializer

from .models import UserProfile
from .utils import encode, decode

JSCODE2SESSION_URL = 'https://api.weixin.qq.com/sns/jscode2session?grant_type=authorization_code'
APPID = settings.WEIXIN_APPID
APPSECRET = settings.WEIXIN_APPSECRET


# 接受小程序发送的code，然后从微信服务器换取用户的微信身份ID
def login(request):
    code = request.GET.get('code')
    url = JSCODE2SESSION_URL + '&appid=' + APPID + '&secret=' + APPSECRET + '&js_code=' + code
    # login(request, user)
    r = requests.get(url).json()
    openid = r['openid']
    session_key = r['session_key']

    try:
        userprofile = UserProfile.objects.get(wxapp_openid=openid)

        return JsonResponse(data={
            'errCode': 0,
            'token': encode(openid),
            'errMsg': "成功",
            "userInfo": userprofile.to_json()
        })
    except UserProfile.DoesNotExist:
        # 用户还未绑定微信账号
        return JsonResponse(data={
            'errCode': 1,
            'token': encode(openid),
            'errMsg': "未绑定账户"
        })
    except Exception as e:
        print(e)
        return JsonResponse(data={
            'errCode': 2,
            'errMsg': "发生错误"
        })


# 绑定网站的用户和微信的用户
@csrf_exempt
def user_bind(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    token = request.POST.get('token')
    print(username, password, token)
    user = authenticate(username=username, password=password)

    if user is None:
        return JsonResponse(data={
            'errCode': 1,
            'errMsg': "用户名或密码错误"
        })
    if user.is_active == False:
        return JsonResponse(data={
            'errCode': 2,
            'errMsg': "该账号已被停用"
        })

    if user.userprofile.wxapp_openid:
        return JsonResponse(data={
            'errCode': 3,
            'errMsg': "该账号已绑定过微信，不能重复绑定"
        })
    openid = decode(token)
    if openid is None:
        return JsonResponse(data={
            'errCode': 4,
            'errMsg': "token已过期"
        })


    existing_users = UserProfile.objects.filter(wxapp_openid=openid)
    if existing_users.exists():
        return JsonResponse(data={
            'errCode': 5,
            'errMsg': "当前微信已绑定过用户，不能重复绑定"
        })

    # 绑定成功
    user.userprofile.wxapp_openid = openid
    user.userprofile.save()
    return JsonResponse(data={
        'errCode': 0,
        'errMsg': "绑定成功",
        'userInfo': user.userprofile.to_json()

    })



# 网站的用户和微信的用户解绑
@csrf_exempt
def user_unbind(request):
    # token = request.POST.get('token')
    # openid = decode(token)
    # existing_user = UserProfile.objects.get(wxapp_openid=openid)
    existing_user=request.user
    if existing_user:
        print(existing_user.userprofile.wxapp_openid)
        existing_user.userprofile.wxapp_openid = None
        existing_user.userprofile.save()
        return JsonResponse(data={
            'errCode': 0,
            'errMsg': "解绑成功"
        })
    else:
        return JsonResponse(data={
            'errCode': 1,
            'errMsg': "错误"
        })
