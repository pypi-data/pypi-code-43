# -*- coding: utf-8 -*-
# @Time     : 2019/4/10 14:32
# @Author   : Run 
# @File     : utils.py
# @Software : PyCharm


import time
import logging
import random
from collections import defaultdict


def gen_logger(logger_name: str = None) -> logging.Logger:
    """
    generate logger by Python standard library `logging`
    todo add other handlers
    Notes:
        1. recommend a third-party module `loguru`, more powerful and pleasant
    """
    # logger
    logger = logging.getLogger(str(random.random()))  # set random name to avoid influence between different loggers
    logger.setLevel(logging.DEBUG)  # set logger's level to the lowest, logging.NOTEST will cause strange situations.
    logger.name = logger_name

    # formatter
    if logger_name is None:
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
    else:
        formatter = logging.Formatter('[%(asctime)s] [%(name)s~%(levelname)s] %(message)s', datefmt='%Y/%m/%d %H:%M:%S')

    # handlers
    # 1. print to screen
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.WARNING)
    logger.addHandler(stream_handler)
    # # 2. print to file
    # file_handler = logging.FileHandler("output.log", encoding='UTF-8', mode='w')
    # file_handler.setFormatter(formatter)
    # file_handler.setLevel(logging.DEBUG)
    # logger.addHandler(file_handler)

    return logger


class Timer:
    """
    timing execution
    using `time.time()`

    Examples
    --------
    timer = Timer()
    <code_block1: to measure>
    timer.toc("block1")
    <code_block2: not to measure>
    timer.tic()
    <code_block3: to measure>
    timer.toc("block3")
    <code_block4: to measure>
    timer.toc("block4")
    timer.total()  # block1's time + block3's time + block4's time

    Notes:
        1. recommend a third-party module `PySnooper`
        2. https://blog.csdn.net/qq_27283619/article/details/89280974 distinguish time.time() with time.perf_counter()
    """
    def __init__(self, logger_func=None):
        self.index = 0
        self.records = []  # [(index, comments, cost_time), ...]
        self.groups = defaultdict(list)  # {group_name: [(index, comments, cost_time), ...], ...}
        self.logger_func = logger_func
        self.prev = time.time()

    def reset(self, drop_logger_func=False):
        self.index = 0
        self.records = []  # [(index, comments, cost_time), ...]
        self.groups = defaultdict(list)  # {group_name: [(index, comments, cost_time), ...], ...}
        if drop_logger_func:
            self.logger_func = None
        self.prev = time.time()

    def tic(self):
        self.prev = time.time()

    def toc(self, comments="", display=True, round_num=3):
        cost_time = round(time.time() - self.prev, round_num)
        self.records.append((self.index, comments, cost_time))
        if display:
            # print("{}. {} {}s".format(self.index, comments, cost_time))
            print("{} {}s".format(comments, cost_time))
            if self.logger_func:
                self.logger_func("{} {}s".format(comments, cost_time))
        self.index += 1
        self.prev = time.time()

    def add(self, group_name, comments="", round_num=3):
        cost_time = round(time.time() - self.prev, round_num)
        self.records.append((self.index, comments, cost_time))
        self.groups[group_name].append((self.index, comments, cost_time))
        self.index += 1
        self.prev = time.time()

    def summary(self, order=True, descending=True):
        """designed for groups"""
        res = [(k, len(v), sum(x[2] for x in v)) for k, v in self.groups.items()]
        if order:
            res = sorted(res, key=lambda x: x[2], reverse=descending)
        for group_name, num, cost_time in res:
            print("{}: {} splits, cost {}s".format(group_name, num, cost_time))

    def total(self):
        return sum(x[2] for x in self.records)

    def order(self, descending=True):
        """

        :param descending: bool
        :return:
        """
        return sorted(self.records, key=lambda x: x[2], reverse=descending)


def timer(func):
    """
    a decorator for timing
    using `time.perf_counter()`
    old function results         new function results
    r1, r2, ..., rn       ->     (r1, r2, ..., rn), cost_time
    Notes:
        1. recommend a third-party module `PySnooper`
        2. similar to `timeit.timeit()`
            e.g. `timeit.timeit('f(x)', 'from __main__ import f, x', number=10)`
    :param func:
    :return:
    """

    def dec(*args, **kwargs):
        t1 = time.perf_counter()
        res = func(*args, **kwargs)
        t2 = time.perf_counter()
        cost_t = t2 - t1
        if cost_t < 1:  # 耗时低于1s重复10遍
            n = 10
        elif cost_t < 10:  # 耗时低于10s重复5遍
            n = 5
        else:  # 耗时超过10s，不进行重复试验
            n = 1
            #
        for _ in range(n - 1):
            t1 = time.perf_counter()
            res = func(*args, **kwargs)
            t2 = time.perf_counter()
            cost_t += t2 - t1
        cost_t /= n
        print("{0} cost time: {1}s, {2} loops".format(func.__name__, t2 - t1, n))
        return res

    return dec








