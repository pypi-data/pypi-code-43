#-*- coding:utf-8 _*-  
'''
@file : str2date.py
@auther : Harrytsz
@time : 2018/11/02
'''

import time


# 格式化url为json
def url_to_json(url):
    params = url.split("?")[1]
    param_arr = params.split("&")
    res = {}
    for i in range(0,len(param_arr)):
        str = param_arr[i].split('=')
        res[str[0]] = str[1]
    return res

# 将位时间戳转换成年月日
def time_stamp(time_num):
    if len(time_num) == 13:
        time_stamp = float(time_num) / 1000
    else:
        time_stamp = float(time_num)
    time_array = time.localtime(time_stamp)
    other_style_time = time.strftime("%Y-%m-%d", time_array)
    return other_style_time


# 将时间转化成年月日时分秒
def time_stamp_YmdHMS(time_num):
    if len(time_num) == 13:
        time_stamp = float(time_num) / 1000
    else:
        time_stamp = float(time_num)
    time_array = time.localtime(time_stamp)
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return other_style_time