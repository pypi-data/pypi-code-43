# -*- coding:utf-8 -*-
'''
@Author: lamborghini1993
@Date: 2019-09-29 20:57:13
@UpdateDate: 2019-09-30 11:26:37
@Description: 
'''

import sys
import time
import traceback


def time2str(ti=-1, timeformat="%Y-%m-%d %H:%M:%S"):
    """时间戳转化为字符串
    
    Keyword Arguments:
        ti {int} -- 传入的时间戳，小于0则为当前时间戳 (default: {-1})
        timeformat {str} -- 字符串格式 (default: {"%Y-%m-%d %H:%M:%S"})
    
    Returns:
        str -- [时间字符串]
    """
    if ti < 0:
        ltime = time.localtime()
    else:
        ltime = time.localtime(ti)
    strtime = time.strftime(timeformat, ltime)
    return strtime


def str2time(sTime, timeformat="%Y-%m-%d %H:%M:%S"):
    """字符串转化为时间戳
    
    Arguments:
        sTime {str} -- 时间字符串
    
    Keyword Arguments:
        timeformat {str} -- 时间字符串格式 (default: {"%Y-%m-%d %H:%M:%S"})
    
    Returns:
        int -- 时间戳
    """
    oTime = time.strptime(sTime, timeformat)
    iTime = int(time.mktime(oTime))
    return iTime


def get_runtime(func):
    """获取func运行时间(装饰器)"""
    def _wrapped_func(*args):
        begintime = time.time()
        result = func(*args)
        endtime = time.time()
        print("%s() %s" % (func.__name__, endtime - begintime))
        return result
    return _wrapped_func


def python_error():
    """打印python异常栈信息
    
    Returns:
        str -- 栈信息 + locals信息
    """
    errTrace = traceback.format_exc()
    tb = sys.exc_info()[-1]
    while tb.tb_next is not None:
        tb = tb.tb_next
    info = tb.tb_frame.f_locals
    sLog = "%s%s" % (errTrace, info)
    return sLog
