# -*- coding: utf-8 -*-
# @Time     : 2019/6/14 23:26
# @Author   : Run 
# @File     : for_arr.py
# @Software : PyCharm

import numpy as np
import pandas as pd
import math 


def find_local_maximum_of_neighborhood(arr, cols, radius=2):
    """
    find local maximum of cols's radius-neighborhood
    :param arr: np.array
    :param cols: list of index, nonnegative
    :param radius: radius of neighborhood
    :return:
    """
    arr = np.array(arr)
    arr1 = np.column_stack([arr[:, max(col - radius, 0): col + radius + 1].max(axis=1) for col in cols])

    return arr1


def find_local_minimum_of_neighborhood(arr, cols, radius=2):
    """
    find local minimum of cols's radius-neighborhood
    :param arr: np.array
    :param cols: list of index, nonnegative
    :param radius: radius of neighborhood
    :return:
    """
    arr = np.array(arr)
    arr1 = np.column_stack([arr[:, col - radius: col + radius + 1].min(axis=1) for col in cols])

    return arr1


def cal_sum_of_neighborhood(arr, cols, radius=2):
    """
    calculate sum of cols's radius-neighborhood
    :param arr: np.array
    :param cols: list of index, nonnegative
    :param radius: radius of neighborhood
    :return:
    """
    arr = np.array(arr)
    arr1 = np.column_stack([arr[:, col - radius: col + radius + 1].sum(axis=1) for col in cols])

    return arr1


def cal_sum_of_fixed_width(arr, width=20):
    """

    :param arr:
    :param width:
    :return:
    """
    arr = np.array(arr)
    n = math.ceil(arr.shape[1] / width)
    arr1 = np.column_stack([arr[:, i*width: (i + 1)*width].sum(axis=1) for i in range(n)])
    
    return arr1


def cal_weighted_mean(arr, weights):
    """
    calculate weighted mean of sliding window for center point
    :param arr: np.array
    :param weights: [i's weight, (i - 1)'s weight, (i - 2)'s weight, ...]
    :return: np.array
    """
    arr = np.array(arr)
    l = len(weights)
    n = sum(weights) * 2 - weights[0]
    s = arr[:, (l-1): (-l+1)] * weights[0]
    for i in range(1, l - 1):
        s += weights[i] * (arr[:, (l - i - 1): (-l-i+1)] + arr[:, (l + i - 1): (-l+i+1)])
    s += weights[-1] * (arr[:, :(2-2*l)] + arr[:, (2*l-2):])
    s = s / n
    return s


def get_nonidentical_columns(arr):
    """

    :param arr:
    :return:
        col_indexes:
        arr1:
    """
    arr = np.array(arr)
    df = pd.DataFrame(arr)
    ser = df.nunique()
    col_indexes = ser[ser > 1].index.tolist()

    return col_indexes, df[col_indexes].values


