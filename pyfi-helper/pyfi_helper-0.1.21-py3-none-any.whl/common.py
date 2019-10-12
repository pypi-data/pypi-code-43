# 和processing 模块有点重叠
from datetime import timedelta, datetime
import scipy.optimize as optimize
import pandas as pd
import numpy as np
import time


class Map(dict):
    """
    Example:
    m = Map({'first_name': 'Eduardo'}, last_name='Pool', age=24, sports=['Soccer'])
    """

    def __init__(self, *args, **kwargs):
        super(Map, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    self[k] = v
                    if isinstance(v, dict):
                        self[k] = Map(v)

        if kwargs:
            for k, v in kwargs.items():
                self[k] = v
                if isinstance(v, dict):
                    self[k] = Map(v)

    def dprint(self):
        for key in self:
            print("      -  " + str(key) + ':' + str(self[key]))

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(Map, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(Map, self).__delitem__(key)
        del self.__dict__[key]


# 打印字典
def dprint(d):
    for key in d:
        print("      -  " + str(key) + ':' + str(d[key]))


def exeTime(func):
    def newFunc(*args, **args2):
        t0 = time.time()
        print("@%s, {%s} start" % (time.strftime("%X", time.localtime()), func.__name__))
        back = func(*args, **args2)
        print("@%s, {%s} end" % (time.strftime("%X", time.localtime()), func.__name__))
        print("@%.3fs taken for {%s}" % (time.time() - t0, func.__name__))
        return back
    
    return newFunc


def nearest(items, pivot):
    """
    the reusult will be a little smaller than pivot with the positive timedelta
    :param items: the samples
    :param pivot: the target
    :return:
    """
    return min(items, key=lambda x: abs((x + timedelta(1) - pivot)))


def get_end_date():
    """确定开始时间，计算最新的已经结算的交易日"""
    try:
        from pyfi import WindHelper
        # 确定结束时间
        # 结束时间为该合约的最后交易日和当前日期的最小值
        last_trade_date = WindHelper.t_days_offset(offset=0, cur_date=datetime.now())
        # 确定结束时间
        if datetime.now().hour >= 19:  # 以晚上19点为界限
            end_date = last_trade_date
        elif datetime.now().date() > last_trade_date.date():  # 当天不是交易日
            end_date = last_trade_date
        else:  # 既非节假日，且当然的数据也没有生成
            end_date = WindHelper.t_days_offset(offset=-1, cur_date=datetime.now())  # datetime类型
    except Exception as e:
        end_date = datetime.now()
    return end_date


def get_date_list(begin_date, end_date):
    # begin_date, end_date是形如‘20160601’的字符串或datetime格式
    date_l = [x for x in list(pd.date_range(start=begin_date, end=end_date))]
    return date_l

