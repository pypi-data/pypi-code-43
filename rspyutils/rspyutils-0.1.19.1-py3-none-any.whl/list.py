# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
import itertools


def get_dedup_list(l):
    """
    list自去重，保持顺序
    :param l:
    :return:
    """
    tmp = list(set(l))
    tmp.sort(key=l.index)
    return tmp


def get_first_col_list(l, n=0):
    """
    获取第n列
    :param l:
    :return:
    """
    return [str(x[n]) for x in l]


def get_diff_lists(l1, l2):
    """
    获取两个list的差集
    l1-l2
    :param l1:
    :param l2:
    :return:
    """
    return list(set(l1).difference(set(l2)))


def get_flat_list(l):
    """
    使用itertools內建模块
    [[],[],[]] -> []
    :param l:
    :return:
    """
    return list(itertools.chain.from_iterable(l))


def get_intersection_list(l1, l2):
    """
    list交集
    :param l:
    :return:
    """
    return list(set(l1).intersection(set(l2)))


def get_union_list(l1, l2):
    """
    list并集,无序
    :param l1:
    :param l2:
    :return:
    """
    return list(set(l1).union(set(l2)))


def get_merge_list(l1, l2):
    """
    list并集,有序
    :param l1:
    :param l2:
    :return:
    """
    return get_dedup_list(l1 + l2)


def check_length(l, length):
    if len(l) < length:
        raise ValueError("len of list is less then {}".format(length))
