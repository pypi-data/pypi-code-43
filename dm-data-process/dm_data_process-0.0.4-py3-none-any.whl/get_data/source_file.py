# coding: utf-8
"""
Created on 2018年5月28日

@author: Damon
"""

import pandas as pd
import chardet
from datetime import datetime
import xlrd


def mkdir(path):  # 判断目录是否存在，不存在则创建
    # 引入模块
    import os
    # 去除首位空格
    path = path.strip()
    # 去除尾部 \ 符号
    path = path.rstrip("\\")

    # 判断路径是否存在
    # 存在     True
    # 不存在   False
    is_exists = os.path.exists(path)

    # 判断结果
    if not is_exists:
        # 如果不存在则创建目录
        # 创建目录操作函数
        os.makedirs(path)

        print(path + ' 创建成功')
        return True
    else:
        # 如果目录存在则不创建，并提示目录已存在
        print(path + ' 目录已存在')
        return False


def check_coding(char_data):  # 判断字符编码类型
    if isinstance(char_data, bytes):
        pass
    else:
        char_data = char_data.encode()
    f_encoding = chardet.detect(char_data)
    return f_encoding['encoding']


# excel
def f_read_excel(read_excel_path, sheet_name=0, header=0):
    data = pd.read_excel(read_excel_path, sheet_name=sheet_name, header=header)
    return data


def f_read_excels(path_list):
    for n in range(len(path_list)):
        if n == 0:
            data = f_read_excel(path_list[n], sheet_name=0, header=0)
        else:
            data_increment = f_read_excel(path_list[n], sheet_name=0, header=0)
            data = data.append(data_increment)
    return data


def f_writer_excel(writer_excel_path, data, sheet_name):
    writer = pd.ExcelWriter(writer_excel_path)
    df1 = pd.DataFrame(data=data)
    df1.to_excel(writer, sheet_name, index=False, encoding='utf-8')
    writer.save()


# csv
def f_read_csv(read_csv_path):
    f = open(read_csv_path)
    try:
        data = pd.read_csv(f, low_memory=False)
    except:
        f2 = open(read_csv_path, "rb")
        d = f2.read()
        f_encoding = check_coding(d)
        f = open(read_csv_path, encoding=f_encoding)
        data = pd.read_csv(f, low_memory=False)
    return data


def f_read_csv_s(path_list):
    for n in range(len(path_list)):
        if n == 0:
            data = f_read_csv(path_list[n])
        else:
            data_increment = f_read_csv(path_list[n])
            data = data.append(data_increment)
    return data


def f_writer_csv(writer_csv_path, data):
    data.to_csv(writer_csv_path, index=False, encoding='ANSI')
    return writer_csv_path

