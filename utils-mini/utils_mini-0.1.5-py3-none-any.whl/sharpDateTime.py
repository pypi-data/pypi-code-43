import datetime
from utilsMini.parse import parseTime, parseTimeStr


class SharpDateTime:
    theTime = None

    def __init__(self, timeStr='', timeFormat='%Y-%m-%d %H:%M:%S'):
        '''
        初始化时间。传入时间字符串，没传的话默认1997-01-01 00:00:01时间
        '''
        if len(timeStr):
            self.theTime = parseTime(timeStr, timeFormat)
        else:
            self.theTime = datetime.datetime.strptime('1997-01-01 00:00:01',
                                                      '%Y-%m-%d %H:%M:%S')

    def now(self):
        '''
        获取当前时间
        '''
        self.theTime = datetime.datetime.now()
        return self

    def addDay(self, days):
        '''
        修改天
        大于0是增加天
        小于0是减少天
        '''
        self.theTime = self.theTime + datetime.timedelta(hours=days)
        return self

    def addMinutes(self, minutes):
        '''
        同上
        '''
        self.theTime = self.theTime + datetime.timedelta(minutes=minutes)
        return self

    def addSeconds(self, seconds):
        '''
        同上
        '''
        self.theTime = self.theTime + datetime.timedelta(seconds=seconds)
        return self

    def addMicroseconds(self, microseconds):
        '''
        同上
        '''
        self.theTime = self.theTime + \
            datetime.timedelta(microseconds=microseconds)
        return self

    def date(self):
        '''
        获取当天的00:00:00
        '''
        self.theTime = self.theTime - datetime.timedelta(
            hours=self.theTime.hour,
            minutes=self.theTime.minute,
            seconds=self.theTime.second,
            microseconds=self.theTime.microsecond)
        return self

    def Last(self):
        '''
        获取当天的23:59:59
        '''
        self.date()
        self.theTime = self.theTime + datetime.timedelta(
            hours=23, minutes=59, seconds=59)
        return self

    def toDateTime(self):
        return self.theTime

    def toString(self, timeFormat='%Y-%m-%d %H:%M:%S'):
        return parseTimeStr(self.theTime, timeFormat)
