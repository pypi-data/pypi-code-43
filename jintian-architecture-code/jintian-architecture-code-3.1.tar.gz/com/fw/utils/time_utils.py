import datetime, time
from enum import Enum
from com.fw.base.base_exception import BaseException


class DateEnum(Enum):
    YMD = "%Y-%m-%d"
    YMDHMS = "%Y-%m-%d %H:%M:%S"


class DateType(Enum):
    DAY = "days"
    HOUR = "hours"
    MINUTE = "minutes"
    SECONDS = "seconds"


class TimeUtils(object):

    @staticmethod
    def getCurrentDateTime(date_enum=DateEnum.YMDHMS):
        '''
                获取当前日期：2013-09-10这样的日期字符串
        '''
        return time.strftime(date_enum.value, time.localtime(time.time()))

    @staticmethod
    def getCurrentHour():
        '''
                获取当前时间的小时数，比如如果当前是下午16时，则返回16
        '''
        currentDateTime = TimeUtils.getCurrentDateTime()
        return currentDateTime[-8:-6]

    @staticmethod
    def getDateElements(sdate):
        '''
                输入日期字符串，返回一个结构体组，包含了日期各个分量
                输入：2013-09-10或者2013-09-10 22:11:22
                返回：time.struct_time(tm_year=2013, tm_mon=4, tm_mday=1, tm_hour=21, tm_min=22, tm_sec=33, tm_wday=0, tm_yday=91, tm_isdst=-1)
        '''
        dformat = ""
        if TimeUtils.judgeDateFormat(sdate) == 0:
            return None
        elif TimeUtils.judgeDateFormat(sdate) == 1:
            dformat = DateEnum.YMD.value
        elif TimeUtils.judgeDateFormat(sdate) == 2:
            dformat = DateEnum.YMDHMS.value
        sdate = time.strptime(sdate, dformat)
        return sdate

    def getDateToNumber(date1):
        '''
                将日期字符串中的减号冒号去掉:
                输入：2013-04-05，返回20130405
                输入：2013-04-05 22:11:23，返回20130405221123
        '''
        return date1.replace("-", "").replace(":", "").replace("", "")

    @staticmethod
    def judgeDateFormat(datestr):
        '''
                判断日期的格式，如果是"%Y-%m-%d"格式则返回1，如果是"%Y-%m-%d %H:%M:%S"则返回2，否则返回0
                参数 datestr:日期字符串
        '''
        try:
            datetime.datetime.strptime(datestr, DateEnum.YMD.value)
            return 1
        except:
            pass

        try:
            datetime.datetime.strptime(datestr, DateEnum.YMDHMS.value)
            return 2
        except Exception as e:
            pass

        return 0

    @staticmethod
    def minusTwoDate(date1, date2):
        '''
                将两个日期相减，获取相减后的datetime.timedelta对象
                对结果可以直接访问其属性days、seconds、microseconds
        '''
        if TimeUtils.judgeDateFormat(date1) == 0 or TimeUtils.judgeDateFormat(date2) == 0:
            return None
        d1Elements = TimeUtils.getDateElements(date1)
        d2Elements = TimeUtils.getDateElements(date2)
        if not d1Elements or not d2Elements:
            return None
        d1 = datetime.datetime(d1Elements.tm_year, d1Elements.tm_mon, d1Elements.tm_mday, d1Elements.tm_hour,
                               d1Elements.tm_min, d1Elements.tm_sec)
        d2 = datetime.datetime(d2Elements.tm_year, d2Elements.tm_mon, d2Elements.tm_mday, d2Elements.tm_hour,
                               d2Elements.tm_min, d2Elements.tm_sec)
        return d1 - d2

    @staticmethod
    def add_date_time_str(num, type: DateType, date=None, format=DateEnum.YMDHMS.value):
        return TimeUtils.add_date_time(num, type, date).strftime(format)

    @staticmethod
    def add_date_time(num, type: DateType, date=None):
        '''
            日期加上或者减去一个数字，返回一个新的日期
            参数date1：要计算的日期
            参数addcount：要增加或者减去的数字，可以为1、2、3、-1、-2、-3，负数表示相减
        '''
        try:
            if type.name == DateType.DAY:
                addtime = datetime.timedelta(days=int(num))
            elif type == DateType.HOUR:
                addtime = datetime.timedelta(hours=int(num))
            elif type == DateType.MINUTE:
                addtime = datetime.timedelta(minutes=int(num))
            elif type == DateType.SECONDS:
                addtime = datetime.timedelta(seconds=int(num))

            if not date:
                date = datetime.datetime.now()
            elif TimeUtils.judgeDateFormat(date) == 1:
                date = datetime.datetime.strptime(date, DateEnum.YMD.value).time()
            elif TimeUtils.judgeDateFormat(date) == 2:
                date = datetime.datetime.strptime(date, DateEnum.YMDHMS.value).time()
            else:
                raise BaseException("非法日期")

            return (date + addtime)
        except Exception as e:
            raise BaseException("日期计算异常...")

    @staticmethod
    def dateDiffInDays(date1, date2):
        '''
                获取两个日期相差的天数，如果date1大于date2，返回正数，否则返回负数
        '''
        minusObj = TimeUtils.minusTwoDate(date1, date2)
        try:
            return minusObj.days
        except Exception as e:
            raise BaseException("日期计算异常...")

    @staticmethod
    def dateDiffInSeconds(date1, date2):
        '''
                获取两个日期相差的秒数
        '''
        minusObj = TimeUtils.minusTwoDate(date1, date2)
        try:
            return minusObj.days * 24 * 3600 + minusObj.seconds
        except Exception as e:
            raise BaseException("日期计算异常...")

    @staticmethod
    def getWeekOfDate(pdate):
        '''
                获取日期对应的周，输入一个日期，返回一个周数字，范围是0~6、其中0代表周日
        '''
        pdateElements = TimeUtils.getDateElements(pdate)

        weekday = int(pdateElements.tm_wday) + 1
        if weekday == 7:
            weekday = 0
        return weekday

    @staticmethod
    def get_ms():
        return int(round(time.time() * 1000))
