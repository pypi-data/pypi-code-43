import time
from datetime import datetime, timedelta
import calendar

import pytz

def get_difftime_in_hours(oldtime, newtime):
    td = datetime.strptime(newtime[:19], "%Y-%m-%dT%H:%M:%S") - datetime.strptime(oldtime[:19], "%Y-%m-%dT%H:%M:%S")
    return float("%.1f" % (td.days * 24 + td.seconds/3600.0))

def get_utc_strtime(strtime):
    return (datetime.strptime(strtime.split("+")[0],'%Y-%m-%dT%H:%M:%S.%f') + \
            timedelta(hours=-1 * int(strtime.split("+")[-1].split(":")[0]))).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]

def get_timestamp_from_strday(day):
    return calendar.timegm(time.strptime(day, "%Y-%m-%d")) * 1000

def get_timestamp_from_strtime(strtime):
    dt = datetime.strptime(strtime.split("+")[0],'%Y-%m-%dT%H:%M:%S.%f') + \
            timedelta(hours=-1 * int(strtime.split("+")[-1].split(":")[0]))
    return int((dt - datetime(1970,1,1)).total_seconds() * 1000)

def get_strtime_from_timestamp(timestamp):
    tz = pytz.timezone("Asia/Shanghai")
    dt = datetime.fromtimestamp(int(int(timestamp)/1000), tz)
    return str(dt).replace(" ", "T").replace("+08:00",".000+08:00")

def convert_strtime_by_tz(strtime):
    ts = get_timestamp_from_strtime(strtime)
    return get_strtime_from_timestamp(ts)
