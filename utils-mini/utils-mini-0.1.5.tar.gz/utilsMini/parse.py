import datetime
import ujson


def parseStr(value, default='') -> str:
    """
    将值转换为int类型
    value：输入不可预期的值
    default：如果处理失败返回此值
    """
    if isinstance(value, str):
        return value
    try:
        return str(value)
    except:
        return default


def parseInt(value, default=0) -> int:
    """
    将值转换为int类型
    value：输入不可预期的值
    default：如果处理失败返回此值
    """
    if isinstance(value, int):
        return value
    try:
        return int(value)
    except:
        return default


def parseFloat(value, default=0) -> float:
    """
    将值转换为Float类型
    value：输入不可预期的值
    default：如果处理失败返回此值
    """
    if isinstance(value, float):
        return value
    try:
        return float(value)
    except:
        pass
    return default


def parseDict(value, default={}) -> dict:
    """
    将值转换为字典类型类型
    value：输入不可预期的值
    default：如果处理失败返回此值
    """
    if isinstance(value, dict):
        return value
    try:
        return dict(value)
    except:
        return default


def parseList(value, default=[]) -> list:
    """
    将值转换为字典类型类型
    value：输入不可预期的值
    default：如果处理失败返回此值
    """
    if isinstance(value, list):
        return value
    try:
        return list(value)
    except:
        return default


def parseTuple(value, default=()) -> tuple:
    """
    将值转换为字典类型类型
    value：输入不可预期的值
    default：如果处理失败返回此值
    """
    if isinstance(value, tuple):
        return value
    try:
        return tuple(value)
    except:
        return default


def parseTime(timeStr, timeFormat='%Y-%m-%d %H:%M:%S'):
    '''
    把字符串转换成时间（datetime）类型
    timeStr： 时间字符串
    timeFormat：字符串格式
    '''
    theTime = datetime.datetime.strptime('1997-01-01 00:00:01',
                                         '%Y-%m-%d %H:%M:%S')
    if isinstance(timeStr, str):
        try:
            if len(timeStr.split(" ")) == 2:
                theTime = datetime.datetime.strptime(timeStr, timeFormat)
            else:
                theTime = datetime.datetime.strptime(timeStr,
                                                     timeFormat.split(" ")[0])
        except:
            pass
    return theTime


def parseTimeStr(dateVal, timeFormat='%Y-%m-%d %H:%M:%S'):
    '''
    把时间类型转换成字符串
    datetime：时间
    timeFormat：字符串格式
    '''
    timeStr = '1997-01-01 00:00:01'
    if isinstance(dateVal, datetime.datetime):
        try:
            timeStr = dateVal.strftime(timeFormat)
        except:
            timeStr = datetime.datetime \
                .strptime('1997-01-01 00:00:01', '%Y-%m-%d %H:%M:%S') \
                .strftime(timeFormat)
    return timeStr


def tryGetValue(dic, key, executor=None, context=None):
    """
    dic:输入的不可预估字典
    需要的key
    executor：需要执行的类型转换方法
    context：类型转换方法的默认参数值
    """
    value = None
    if isinstance(dic, dict):
        value = dic.get(key)
    if executor:
        if context:
            return executor(value, context)
        else:
            return executor(value)
    return value


def parseJsonStr(obj, format=False):
    '''
    转换为json字符串，含中文
    '''
    return ujson.dumps(obj,
                       ensure_ascii=False,
                       indent=None if format is False else 4)


def parseJsonobj(obj):
    '''
    json字符串转换为字典，含中文
    '''
    if isinstance(obj, str):
        try:
            return ujson.loads(obj)
        except:
            return None
    return None
