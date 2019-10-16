# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""


def get_read_file_func(spark, read_type='hive', db="ods_samh", hdfs_path="/user/hive/warehouse/ods_samh.db"):
    """
    读取数据的函数
    :param read_type: 读取方式（hive或者hdfs)
    :return:
    """
    if read_type == 'hive':
        read_func = lambda x: spark.table("{}.{}".format(db, x))
    elif read_type == 'hdfs':
        read_func = lambda x: spark.read.option("mergeSchema", "true").parquet(
            "{}/{}".format(hdfs_path, x))
    else:
        raise ValueError("wrong read file type")
    return read_func
