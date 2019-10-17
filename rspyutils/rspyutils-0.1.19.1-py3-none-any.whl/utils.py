# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
import hashlib
import time


def hashstr(s, nr_bins):
    return str(int(hashlib.md5(s.encode('utf-8')).hexdigest(), 16) % (nr_bins - 1) + 1)


def print_run_time(func):
    def wrapper(*args, **kw):
        local_time = time.time()
        func(*args, **kw)
        print('Current function : {function}, time used : {temps}'.format(
            function=func.__name__, temps=time.time() - local_time))

    return wrapper


def get_top_k(row, k, mininum, rank=0, forbidden=[]):
    """从1*m的系数矩阵中获得top k的指标

    Args:
        row(csr_matrix) :- shape=[1, any]
        k(int) :- 选取的数目上限
        mininum(int) :- 下限
        rank(int) :- 只选择前rank列的,如果rank>0
        forbidden(iterables) :- 不可以选择的
    Returns:
        top k 数值的列号
    """
    if rank > 0:
        row = row[:, :rank]
    rec_num = min(k, row.count_nonzero())
    if rec_num < mininum:
        return []
    pair = zip(row.data, row.indices)
    indices = sorted(pair, key=lambda x: x[0], reverse=True)
    indices = [ind[1] for ind in indices if ind[1] not in forbidden]
    rec_num = min(rec_num, len(indices))
    if rec_num < mininum:
        return []
    return indices[:rec_num]


def get_top_k2(data, indices, k, mininum, rank=0, forbidden=[]):
    """从1*m的系数矩阵中获得top k的指标

    Args:
        data(np.ndarray) :- shape=(any,)
        indices(np.ndarray) :- shape=(any,)
        k(int) :- 选取的数目上限
        mininum(int) :- 下限
        rank(int) :- 只选择前rank列的,如果rank>0
        forbidden(iterables) :- 不可以选择的
    Returns:
        top k 数值的列号
    """
    rec_num = min(k, len(data))
    if rec_num < mininum:
        return []
    pair = zip(data, indices)
    indices = sorted(pair, key=lambda x: x[0], reverse=True)
    indices = [ind[1] for ind in indices if ind[1] not in forbidden and ind[1] <= rank]
    rec_num = min(rec_num, len(indices))
    if rec_num < mininum:
        return []
    return indices[:rec_num]

