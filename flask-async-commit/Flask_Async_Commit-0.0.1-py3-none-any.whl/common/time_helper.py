# coding: utf-8
import datetime
import time

PER_DAY_SECONDS = 24 * 3600
EAST_8_ZONE_SECONDS = 8 * 3600


def formatted_time_list(start_time, end_time=None, form='%Y-%m-%d'):
    """
    给出两个时间戳之间所有的格式化的时间，包括这两个日期
    :param start_time:起始时间，不能为空
    :param end_time:结束时间，可为空，若为空则做格式转换
    :param form: 默认格式是'%Y-%m-%d'
    :return:总是list，元素为string
    """
    if end_time is None:
        return to_formatted_time(start_time, form)
    start_time = datetime.datetime.fromtimestamp(int(start_time))
    end_time = datetime.datetime.fromtimestamp(int(end_time))
    date_list = []
    while start_time <= end_time:
        date_list.append(start_time.strftime(form))  # 日期存入列表
        start_time += datetime.timedelta(days=+1)  # 日期加一天
    return date_list


def day_begin(t):
    """
    返回给定时间的凌晨0点的时间戳
    :param t: 时间戳，int/float/str都可
    :return: int型时间戳
    """
    return ((int(t) + EAST_8_ZONE_SECONDS) // PER_DAY_SECONDS) * PER_DAY_SECONDS - EAST_8_ZONE_SECONDS


def day_end(t):
    """
    返回给定时间的24点（第二天的0点）的时间戳
    :param t: 时间戳，int/float/str都可
    :return: int型时间戳
    """
    return ((int(t) + EAST_8_ZONE_SECONDS) // PER_DAY_SECONDS) * PER_DAY_SECONDS - EAST_8_ZONE_SECONDS + PER_DAY_SECONDS


def int_timestamp():
    """
    返回现在的int型的时间戳
    :return: 返回现在的int型的时间戳
    """
    return int(time.time())


def compare_date(time1, time2, form='%Y-%m-%d'):
    """
    给出两个时间，比较大小
    :param time1: 一个时间
    :param time2: 两个时间
    :param form: 时间的格式，方便做格式转换
    :return: time1?time2，大于1， 小于-1， 等于0
    """
    time1 = time.mktime(time.strptime(time1, form))
    time2 = time.mktime(time.strptime(time2, form))
    if time1 > time2:
        return 1
    elif time1 < time2:
        return -1
    else:
        return 0


def to_int_timestamp(t, form='%Y-%m-%d'):
    """
    给一个格式化的时间，返回其int型时间戳
    :param t: 格式化的时间（str）
    :param form: 时间的格式，默认为 %Y-%m-%d
    :return: int型时间戳
    """
    return int(time.mktime(time.strptime(t, form)))


def to_formatted_time(t, form='%Y-%m-%d'):
    """
    给出时间戳，返回格式化的时间
    :param t: 时间戳，int/float/str都可
    :param form: 期望的时间格式
    :return: 格式化的时间（str）
    """
    return datetime.datetime.fromtimestamp(int(t)).strftime(form)


if __name__ == '__main__':
    print("to_int_timestamp('2019-7-31')\n", to_int_timestamp('2019-7-31'))
    print("to_int_timestamp('2019.7.31', '%Y.%m.%d')\n", to_int_timestamp('2019.7.31', '%Y.%m.%d'))
    print("compare_date('2019-7-20', '2019-7-31')\n", compare_date('2019-7-20', '2019-7-31'))
    print("compare_date('2019.7.31', '2019.7.31', '%Y.%m.%d')\n", compare_date('2019.7.31', '2019.7.31', '%Y.%m.%d'))
    print("compare_date('2019-7-20', '2019-7-10', '%Y.%m.%d')\n", compare_date('2019-7-20', '2019-7-10', '%Y-%m-%d'))
    print("formatted_time_list('1564538424', '1564797624', '%Y-%m-%d')\n", \
        formatted_time_list('1564538424', '1564797624', '%Y-%m-%d'))
    print("formatted_time_list('1564538424', '1564797624', '%Y.%m.%d')\n", \
        formatted_time_list('1564538424', '1564797624', '%Y.%m.%d'))

