#!usr/bin/env python
#-*- coding:utf-8 _*-
"""
@file: DateUtils.py
@time: 2019/05/16
"""
import time,datetime

class DateUtils(object):

    def unix_millisecond(self):
        '''时间戳，毫秒
        '''
        return int(time.time() * 1000)

    def unix_second(self):
        '''时间戳，秒'''
        return int(time.time())

    def in_hours(self,hour=-1):
        '''
        最近几小时，提前传负数
        :param hour:
        :return:
        '''
        return (datetime.datetime.now() + datetime.timedelta(hours=hour)).strftime("%Y-%m-%d %H:%M:%S")

    def in_days(self,day=-1):
        '''
        最近几天，提前传负数
        :param day:
        :return:
        '''
        return (datetime.datetime.now() + datetime.timedelta(days=day)).strftime("%Y-%m-%d %H:%M:%S")

    def in_minutes(self,minute=-1):
        '''
        最近几分钟，提前传负数
        :param day:
        :return:
        '''
        return (datetime.datetime.now() + datetime.timedelta(minutes=minute)).strftime("%Y-%m-%d %H:%M:%S")

    def unix_to_strtime(self,unix):
        '''
        unix时间戳转换成 时间格式
        :param unixm:  int  毫秒先除以1000
        :return:  str  2018-03-01 00:00:11
        '''
        if isinstance(unix,int):
            if len(str(unix)) >10:    #毫秒级
                unix = unix/1000
            time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(unix))
            return time_str

    def nowtime_to_timestr(self):
        '''
        返回当前的时间 str
        :return:  str  2018-03-01 00:00:11
        '''
        timestr = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return timestr

    def timestr_to_unix(self,timestr,flag='S'):
        '''
        时间字符转unix
        :param timestr:  str 2018-03-01 00:00:11
        :param flag:  S 秒级  M 毫秒级，默认S
        :return:  str  unix
        '''
        unix_time = int(time.mktime(time.strptime(timestr, "%Y-%m-%d %H:%M:%S")))
        if flag == 'M':
            unix_time = unix_time * 1000
        return unix_time


if __name__ == '__main__':
    print(DateUtils().nowtime_to_timestr())



