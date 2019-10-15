import re
class TimeSpan(object):
    """TimeSpan CodeStyle Like DotNet By Chenyi"""
    _totalMillisecond=0
    def __init__(self,hour=0,minute=0,second=0,Millisecond=0,day=0):
        self._totalMillisecond+=hour*60*60*1000
        self._totalMillisecond+=minute*60*1000
        self._totalMillisecond+=second*1000
        self._totalMillisecond+=Millisecond
        self._totalMillisecond+=day*24*60*60*1000
        self.TotalSecond=int(self._totalMillisecond/1000)
        self.TotalMinute=int(self.TotalSecond/60)
        self.TotalHour=int(self.TotalMinute/60)
        self.TotalDay=int(self.TotalHour/24)
        self.TotalMillisecond=self._totalMillisecond
        pass

    def AddDays(self,count):
        return TimeSpan(Millisecond=self._totalMillisecond+count*24*60*60*1000)

    def AddHours(self,count):
        return TimeSpan(self._totalMillisecond+count*60*60*1000)

    def AddMinutes(self,count):
        return TimeSpan(self._totalMillisecond+count*60*1000)
    
    def AddSeconds(self,count):
        return TimeSpan(self._totalMillisecond+count*1000)

    def AddMilliseconds(self,count):
        return TimeSpan(self._totalMillisecond+count)

    def __add__(self, obj):
        if type(obj) is TimeSpan:
            r=self._totalMillisecond + obj.TotalMillisecond
            return TimeSpan(Millisecond=r)
        else:
            raise Exception("不是TimeSpan类型!")
    
    def __sub__(self,obj):
        if type(obj) is TimeSpan:
            if obj.TotalMillisecond>self._totalMillisecond:
                raise Exception("结果是负的!")
            else:
                r=self._totalMillisecond - obj.TotalMillisecond
                return TimeSpan(Millisecond=r)
        else:
            raise Exception("不是TimeSpan类型!")

    def __lt__(self,value):
        return self.TotalMillisecond<value.TotalMillisecond
    def __gt__(self,value):
        return self.TotalMillisecond>value.TotalMillisecond
    def __le__(self,value):
        return self.TotalMillisecond<=value.TotalMillisecond
    def __ge__(self,value):
        return self.TotalMillisecond>=value.TotalMillisecond
    def __eq__(self,value):
        return self.TotalMillisecond==value.TotalMillisecond
    def __ne__(self,value):
        return self.TotalMillisecond!=value.TotalMillisecond

    @staticmethod
    def Convert(dateStr="",formatStr="")->"TimeSpan":
        if len(formatStr)!=len(dateStr):
            raise Exception()
        _day=0
        _hour=0
        _minute=0
        _second=0
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
        return TimeSpan(_hour,_minute,_second,_day)

    @staticmethod
    def AutoConvert(timeStr:str):
        if not timeStr:
            return TimeSpan(0,0,0)
        #region 时分秒
        r=re.search("(\\d{1,2}):(\\d{1,2}):(\\d{1,2})",timeStr)
        if r:
            _dt="{}:{}:{}".format(
                r.group(1).zfill(2)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                )
            return TimeSpan.Convert(_dt,"HH:mm:ss")
        r=re.search("(\\d{1,2})时(\\d{1,2})分(\\d{1,2})秒",timeStr)
        if r:
            _dt="{}:{}:{}".format(
                r.group(1).zfill(2)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                )
            return TimeSpan.Convert(_dt,"HH:mm:ss")
        r=re.search("(\\d{1,2})小时(\\d{1,2})分(\\d{1,2})秒",timeStr)
        if r:
            _dt="{}:{}:{}".format(
                r.group(1).zfill(2)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                )
            return TimeSpan.Convert(_dt,"HH:mm:ss")
        r=re.search("(\\d{1,2})小时(\\d{1,2})分钟(\\d{1,2})秒",timeStr)
        if r:
            _dt="{}:{}:{}".format(
                r.group(1).zfill(2)
                ,r.group(2).zfill(2)
                ,r.group(3).zfill(2)
                )
            return TimeSpan.Convert(_dt,"HH:mm:ss")

        #endregion

        #region 分秒
        r=re.search("(\\d{1,2}):(\\d{1,2})",timeStr)
        if r:
            _dt="00:{}:{}".format(
                r.group(1).zfill(2)
                ,r.group(2).zfill(2)
                )
            return TimeSpan.Convert(_dt,"HH:mm:ss")
        r=re.search("(\\d{1,2})分(\\d{1,2})秒",timeStr)
        if r:
            _dt="00:{}:{}".format(
                r.group(1).zfill(2)
                ,r.group(2).zfill(2)
                )
            return TimeSpan.Convert(_dt,"HH:mm:ss")
        r=re.search("(\\d{1,2})分钟(\\d{1,2})秒",timeStr)
        if r:
            _dt="00:{}:{}".format(
                r.group(1).zfill(2)
                ,r.group(2).zfill(2)
                )
            return TimeSpan.Convert(_dt,"HH:mm:ss")
        r=re.search("(\\d+):(\\d{1,2})",timeStr)
        if r:
            m=int(r.group(1))
            s=int(r.group(2))
            return TimeSpan(0,m,s)
        #endregion
        #region 只有秒
        r=re.search("(\\d{1,2})秒",timeStr)
        if r:
            _dt="00:00:{}".format(
                r.group(1).zfill(2)
                )
            return TimeSpan.Convert(_dt,"HH:mm:ss")
        r=re.search("(\\d{3,4,5,6,7,8,9,10})秒",timeStr)
        if r:
            return TimeSpan(second=int(r.group(1)))
        #endregion

        #region 单独情况判断
        hint=0
        mint=0
        sint=0
        h=re.search("(\\d+)(时|小时)",timeStr)
        if h:
            hint=int(h.group(1))
        m=re.search("(\\d+)(分|分钟)",timeStr)
        if m:
            mint=int(m.group(1))
        s=re.search("(\\d+)(秒|分钟)",timeStr)
        if s:
            sint=int(s.group(1))
        return TimeSpan(hint,mint,sint)
        #endregion