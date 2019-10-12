# -*- coding: utf-8 -*-
# @Time     : 2019/10/5 10:57
# @Author   : Run 
# @File     : __init__.py.py
# @Software : PyCharm


from RunToolkit.for_df.transform import Cube
import numpy as np
import pandas as pd
from string import ascii_lowercase


df2dict = Cube().df2dict


def gen_df(row_num, col_num, lb=0, ub=100):
    """
    generate dataframe consist of int data and lowercase_headers
    :param row_num:
    :param col_num:
    :param lb: lower bound
    :param ub: upper bound
    :return:
    """
    shape = (row_num, col_num)
    data = np.random.randint(lb, ub, shape)
    cols = list(ascii_lowercase[:col_num])
    df = pd.DataFrame(data, columns=cols)
    print("shape:", df.shape)
    print(df.head(2))
    return df


def compare_df(df1: pd.DataFrame, df2: pd.DataFrame, delta=1e-6) -> bool:
    """
    Check if two DataFrames are the same.
    Notes:
        1. todo `type(1.0) != type(1)`, but `1.0 == 1`
        2. todo speed up
    :param df1:
    :param df2:
    :param delta: precision of float
    :return:
    """
    if df1.shape != df2.shape:
        print("different shape")
        print("df1: {}".format(df1.shape))
        print("df2: {}".format(df2.shape))
        return False
    if df1.dtypes.tolist() != df2.dtypes.tolist():
        print("different dtypes")
        print("df1: {}".format(df1.dtypes))
        print("df2: {}".format(df2.dtypes))
        return False
    if df1.columns.names != df2.index.names:
        print("different header names")
        print("df1: {}".format(df1.columns.names))
        print("df2: {}".format(df2.columns.names))
        return False
    if df1.columns.tolist() != df2.columns.tolist():
        print("different header")
        print("df1: {}".format(df1.columns))
        print("df2: {}".format(df2.columns))
        return False
    if df1.index.names != df2.index.names:
        print("different index names")
        print("df1: {}".format(df1.index.names))
        print("df2: {}".format(df2.index.names))
        return False
    if df1.index.tolist() != df2.index.tolist():
        print("different index")
        return False
    #
    m, n = df1.shape
    for i in range(m):
        for j in range(n):
            x1, x2 = df1.iloc[i, j], df2.iloc[i, j]
            type1, type2 = type(x1), type(x2)
            if type1 != type2:
                print("different type")
                print("type(df1[{}, {}]): {}".format(i, j, type1))
                print("type(df2[{}, {}]): {}".format(i, j, type2))
                return False
            if isinstance(x1, float) or isinstance(x1, np.floating):
                if abs(x1 - x2) > delta:
                    print("different float value")
                    print("df1[{}, {}]: {}".format(i, j, x1))
                    print("df2[{}, {}]: {}".format(i, j, x2))
                    return False
            else:
                if str(x1) != str(x2):
                    print("different value")
                    print("df1[{}, {}]: {}".format(i, j, x1))
                    print("df2[{}, {}]: {}".format(i, j, x2))
                    return False
    print("df1 and df2 are the same.")
    return True


def merge_by(df1: pd.DataFrame, df2: pd.DataFrame, condition):
    """
    similar to conditional join in sql
    :param df1:
    :param df2:
    :param condition:
    :return:
    """
    pass  # todo
