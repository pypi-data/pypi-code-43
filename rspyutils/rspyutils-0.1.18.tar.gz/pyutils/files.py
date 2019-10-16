# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
import os
import re
import pandas as pd
from pyutils import dates


def file_repalce(source, dest):
    os.replace(source, dest)


def get_dir_path(file):
    return os.path.abspath(os.path.dirname(file))


def get_updir_path(file):
    return os.path.dirname(os.path.dirname(os.path.abspath(file)))


def get_upupdir_path(file):
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(file))))


def get_dir_file_name(file_dir, suffix=".txt"):
    L = []
    if suffix:
        for files in os.listdir(file_dir):
            file_path = os.path.join(file_dir, files)
            if os.path.isfile(file_path) and os.path.splitext(file_path)[1] == suffix:
                L.append(file_path)
    else:
        for files in os.listdir(file_dir):
            file_path = os.path.join(file_dir, files)
            if os.path.isfile(file_path):
                L.append(file_path)
    return L


def get_csv_data(file_path="origin_data_2019-08-01.csv"):
    df = pd.read_csv(file_path)
    return df


def get_pickle_data(file_path="origin_data_2019-08-01.plk"):
    df = pd.read_pickle(file_path)
    return df


def get_multi_csv_data(file_path, max_len=-1):
    file_num = 0
    frames = []
    for x in get_dir_file_name(file_path, suffix=".csv"):
        frames.append(pd.read_csv(x))
        file_num += 1
        if file_num >= max_len:
            break
    result = pd.concat(frames)
    return result


def get_multi_pickle_data(file_path, max_len=-1):
    file_num = 0
    frames = []
    for x in get_dir_file_name(file_path, suffix=".pkl"):
        frames.append(pd.read_pickle(x))
        file_num += 1
        if file_num >= max_len:
            break
    result = pd.concat(frames)
    return result


def rm_file_by_date(file_path, date_len=30, suffix=".csv"):
    thr_date = dates.get_before_date(date_len).strftime("%Y-%m-%d")
    for x in get_dir_file_name(file_path, suffix=suffix):
        file_date = re.findall(r"(\d{4}-\d{1,2}-\d{1,2})", x)
        if file_date and dates.get_date_compare(thr_date, file_date[0]):
            os.remove(x)


if __name__ == "__main__":
    rm_file_by_date(file_path="/home/zhanglanhui/recommend_workspace/rank/samh/ctr/xgb-lr/train/csv1",
                    date_len=35,
                    suffix=".csv")
