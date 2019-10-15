import time
import datetime
import re
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from ExObject.TimeSpan import *
class DateTime(object):
    """DateTime CodeStyle Like DotNet By Chenyi"""
    _dateTime=datetime.datetime.now()

    def __init__(self,year=1971,month=1,day=1,hour=0,minute=0,second=0,datetimeParam=None):
        self._dateTime=datetime.datetime(year,month,day,hour,minute,second)
        if datetimeParam:
            self._dateTime=datetimeParam

        self.Day=self._dateTime.day
        self.Month=self._dateTime.month
        self.Year=self._dateTime.year
        self.Hour=self._dateTime.hour
        self.Minute=self._dateTime.minute
        self.Second=self._dateTime.second
        self.Millisecond=self._dateTime.microsecond

    def AddDays(self,count:int)->"DateTime":
        return DateTime(datetimeParam=self._dateTime+relativedelta(days=count))
    
    def AddMonths(self,count:int)->"DateTime":
        return DateTime(datetimeParam=self._dateTime+relativedelta(months=count))

    def AddYears(self,count:int)->"DateTime":
        return DateTime(datetimeParam=self._dateTime+relativedelta(years=count))

    def AddHours(self,count:int)->"DateTime":
        return DateTime(datetimeParam=self._dateTime+relativedelta(hours=count))

    def AddMinutes(self,count:int)->"DateTime":
        return DateTime(datetimeParam=self._dateTime+relativedelta(minutes=count))

    def AddSeconds(self,count:int)->"DateTime":
        return DateTime(datetimeParam=self._dateTime+relativedelta(seconds=count))

    def AddMilliseconds(self,count:int)->"DateTime":
        return DateTime(datetimeParam=self._dateTime+relativedelta(microseconds=count*1000))

    def Date(self)->"DateTime":
        """仅获得日期部分"""
        return DateTime(self.Year,self.Month,self.Day)

    def MonthFirstDay(self)->"DateTime":
        return DateTime(self.Year,self.Month)

    def MonthLastDay(self)->"DateTime":
        return DateTime(self.Year,self.Month).AddMonths(1).AddDays(-1)

    def ToString(self,formatStr="yyyy-MM-dd HH:mm:ss")->str:
        """以指定格式序列化DateTime对象,默认为yyyy-MM-dd HH:mm:ss yyyy=年份 MM=月 dd=日期 HH=24小时制时 hh=12小时制时 mm=分钟 ss=秒"""
        if formatStr=="r":
            GMT_FORMAT = '%a, %d %b %Y %H:%M:%S GMT+0800 (CST)'
            return self._dateTime.strftime(GMT_FORMAT)
        result=formatStr
        if "yyyy" in result:
            result=result.replace("yyyy",str(self._dateTime.year))
        if "MM" in result:
            result=result.replace("MM",str(self._dateTime.month).zfill(2))
        if "dd" in result:
            result=result.replace("dd",str(self._dateTime.day).zfill(2))
        if "HH" in result:
            result=result.replace("HH",str(self._dateTime.hour).zfill(2))
        if "hh" in result:
            _hour=self._dateTime.hour
            if _hour>12:
                result=result.replace("hh",str(self._dateTime.hour-12).zfill(2))
            else:
                result=result.replace("hh",str(self._dateTime.hour).zfill(2))
        if "mm" in result:
            result=result.replace("mm",str(self._dateTime.minute).zfill(2))
        if "ss" in result:
            result=result.replace("ss",str(self._dateTime.second).zfill(2))
        return result

    def TimeStamp(self)->str:
        """获得DateTime对象时间的时间戳"""
        return str(int(self._dateTime.timestamp()*1000))

    def TimeStampLong(self)->int:
        """获得DateTime对象时间的时间戳"""
        return int(self._dateTime.timestamp()*1000)

    def TotalMillisecond(self):
        return int(self._dateTime.timestamp()*1000)

    def __str__(self):
        return self.ToString()
    def __repr__(self):
        return self.ToString()
    def __lt__(self,value):
        return self.TotalMillisecond()<value.TotalMillisecond()
    def __gt__(self,value):
        return self.TotalMillisecond()>value.TotalMillisecond()
    def __le__(self,value):
        return self.TotalMillisecond()<=value.TotalMillisecond()
    def __ge__(self,value):
        return self.TotalMillisecond()>=value.TotalMillisecond()
    def __eq__(self,value):
        return self.TotalMillisecond()==value.TotalMillisecond()
    def __ne__(self,value):
        return self.TotalMillisecond()!=value.TotalMillisecond()
    def __add__(self,value):
        if type(value) is TimeSpan:
            return self.AddMilliseconds(value.TotalMillisecond)
        else:
            raise Exception("不是TimeSpan类型!")
    def __sub__(self,value):
        if type(value) is TimeSpan:
            return self.AddMilliseconds(-value.TotalMillisecond)
        elif type(value) is DateTime:
            if value>self:
                r=value.TotalMillisecond()-self.TotalMillisecond()
                return TimeSpan(Millisecond=r)
            else:
                r=self.TotalMillisecond()-value.TotalMillisecond()
                return TimeSpan(Millisecond=r)
        else:
            raise Exception("不是TimeSpan类型!")

    @staticmethod
    def Now():
        """获得当前时间的DateTime对象"""
        return DateTime(datetimeParam=datetime.datetime.now())

    @staticmethod
    def Today():
        """获得当前时间的DateTime对象"""
        return DateTime(datetimeParam=datetime.datetime.now()).Date()

    @staticmethod
    def DaysInMonth(year,month):
        """获得指定月份的天数"""
        return DateTime(year,month).AddMonths(1).AddDays(-1).Day

    @staticmethod
    def DaysInYear(year):
        """获得指定年份的天数"""
        total=0
        for i in range(1,13):
            total+=DateTime.DaysInMonth(year,i)
        return total

    @staticmethod
    def FromTimestamp(timestamp):
        return DateTime().AddMilliseconds(timestamp).AddDays(-365).AddHours(8)

    @staticmethod
    def FromTimestampToStr(timestamp,defalt="")->str:
        try:
            if isinstance(timestamp,int):
                return DateTime.FromTimestamp(timestamp).ToString("yyyy-MM-dd")
            elif isinstance(timestamp,str):
                return DateTime.FromTimestamp(int(timestamp)).ToString("yyyy-MM-dd")
            else:
                return defalt
        except:
            return defalt

    @staticmethod
    def Convert(dateStr="",formatStr="")->"DateTime":
        """
        Convert Str To DateTime Object
        """
        if len(formatStr)!=len(dateStr):
            raise Exception()
        _year=1970
        _month=1
        _day=1
        _hour=0
        _minute=0
        _second=0
        if "yyyy" in formatStr:
            pos=formatStr.index("yyyy")
            _year=int(dateStr[pos:pos+4])
        if "MM" in formatStr:
            pos=formatStr.index("MM")
            _month=int(dateStr[pos:pos+2])
        if "dd" in formatStr:
            pos=formatStr.index("dd")
            _day=int(dateStr[pos:pos+2])
        if "HH" in formatStr:
            pos=formatStr.index("HH")
            _hour=int(dateStr[pos:pos+2])
        if "hh" in formatStr:
            pos=formatStr.index("hh")
            _hour=int(dateStr[pos:pos+2])
        if "mm" in formatStr:
            pos=formatStr.index("mm")
            _minute=int(dateStr[pos:pos+2])
        if "ss" in formatStr:
            pos=formatStr.index("ss")
            _second=int(dateStr[pos:pos+2])
        return DateTime(_year,_month,_day,_hour,_minute,_second)

    @staticmethod
    def AutoConvert(dateStr:str):
        """
        Auto Convert Str To DateTime Object
        """
        def GetMonthFromEng(str):
            dic={
                "jan":"01",
                "feb":"02",
                "mar":"03",
                "apr":"04",
                "may":"05",
                "jun":"06",
                "jul":"07",
                "aug":"08",
                "sep":"09",
                "oct":"10",
                "nov":"11",
                "dec":"12",
                "January":"01",
                "February":"02",
                "March":"03",
                "April":"04",
                "May":"05",
                "June":"06",
                "July":"07",
                "August":"08",
                "September":"09",
                "October":"10",
                "November":"11",
                "December":"12"
                }
            return dic[str]
        if not dateStr:
            return DateTime()
        #region 包含完整时间
        r=re.search("([0-9]{4})\\-([0-9]{1,2})\\-([0-9]{1,2}) (\\d{1,2}):(\\d{1,2}):(\\d{1,2})",dateStr)
        if r:
            _dt="{}-{}-{} {}:{}:{}".format(
                r.group(1)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                ,r.group(4).zfill(2)
                ,r.group(5).zfill(2)
                ,r.group(6).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([0-9]{4})\\/([0-9]{1,2})\\/([0-9]{1,2}) (\\d{1,2}):(\\d{1,2}):(\\d{1,2})",dateStr)
        if r:
            _dt="{}-{}-{} {}:{}:{}".format(
                r.group(1)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                ,r.group(4).zfill(2)
                ,r.group(5).zfill(2)
                ,r.group(6).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日 (\\d{1,2}):(\\d{1,2}):(\\d{1,2})",dateStr)
        if r:
            _dt="{}-{}-{} {}:{}:{}".format(
                r.group(1)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                ,r.group(4).zfill(2)
                ,r.group(5).zfill(2)
                ,r.group(6).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日(\\d{1,2}):(\\d{1,2}):(\\d{1,2})",dateStr)
        if r:
            _dt="{}-{}-{} {}:{}:{}".format(
                r.group(1)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                ,r.group(4).zfill(2)
                ,r.group(5).zfill(2)
                ,r.group(6).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([0-9]{4})([0-9]{1,2})([0-9]{1,2}) (\\d{1,2}):(\\d{1,2}):(\\d{1,2})",dateStr)
        if r:
            _dt="{}-{}-{} {}:{}:{}".format(
                r.group(1)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                ,r.group(4).zfill(2)
                ,r.group(5).zfill(2)
                ,r.group(6).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([1-2][0-9]{3})([0-1][0-9])([0-3][0-9])([0-2][0-9])([0-5][0-9])([0-5][0-9])",dateStr)
        if r:
            _dt="{}-{}-{} {}:{}:{}".format(
                r.group(1)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                ,r.group(4).zfill(2)
                ,r.group(5).zfill(2)
                ,r.group(6).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        #endregion

        #region 只包含年月日
        r=re.search("([0-9]{4})\\-([0-9]{1,2})\\-([0-9]{1,2})",dateStr)
        if r:
            _dt="{}-{}-{} 00:00:00".format(
                r.group(1)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([0-9]{4})\\/([0-9]{1,2})\\/([0-9]{1,2})",dateStr)
        if r:
            _dt="{}-{}-{} 00:00:00".format(
                r.group(1)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([0-9]{4})年([0-9]{1,2})月([0-9]{1,2})日",dateStr)
        if r:
            _dt="{}-{}-{} 00:00:00".format(
                r.group(1)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([1-2][0-9]{3})([0-1][0-9])([0-3][0-9])",dateStr)
        if r:
            _dt="{}-{}-{} 00:00:00".format(
                r.group(1)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        #endregion

        #region 只包含年月
        r=re.search("([0-9]{4})\\-([0-9]{1,2})",str)
        if r:
            _dt="{}-{}-01 00:00:00".format(
                r.group(1)
                ,r.group(2).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([0-9]{4})\\/([0-9]{1,2})",str)
        if r:
            _dt="{}-{}-01 00:00:00".format(
                r.group(1)
                ,r.group(2).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([0-9]{4})年([0-9]{1,2})月",str)
        if r:
            _dt="{}-{}-01 00:00:00".format(
                r.group(1)
                ,r.group(2).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("([1-2][0-9]{3})([0-1][0-9])",str)
        if r:
            _dt="{}-{}-01 00:00:00".format(
                r.group(1)
                ,r.group(2).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec).*?([0-9]{1,2}).*?([1-2][0-9]{3})", str.lower())
        if r:
            _dt="{}-{}-{} 00:00:00".format(
                r.group(3)
                ,GetMonthFromEng(r.group(1)).zfill(2)
                ,r.group(2).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        r=re.search("(January|February|March|April|May|June|July|August|September|October|November|December).*?([0-9]{1,2}).*?([1-2][0-9]{3})", str.lower())
        if r:
            _dt="{}-{}-{} 00:00:00".format(
                r.group(3)
                ,GetMonthFromEng(r.group(1)).zfill(2)
                ,r.group(2).zfill(2)
                )
            return DateTime.Convert(_dt,"yyyy-MM-dd HH:mm:ss")
        #endregion