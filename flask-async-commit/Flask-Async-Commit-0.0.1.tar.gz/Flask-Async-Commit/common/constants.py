# -*- coding:utf-8 -*-

RESP_SUCCESS = 200
RESP_FAILED = 403
RESP_ERROR = 500

ERROR_MSG_MAP = {
    200: 'success',
    201: 'created',
    401: '未提供认证信息',
    402: '认证信息过期，请重新登录',
    403: '错误的认证信息',
    404: '请求内容不存在',
    405: '不允许的操作',
    406: '店铺不存在',
    500: '请求错误，请联系管理员',
    501: 'JSON格式错误',
}


ZONE_STRUCT = {
    2: '大悦城',
    1: '楼层',
    0: '区域'
}

ERROR_MSG_MAP_ZONE = {
    601: 'exist alive devices in zone'}
