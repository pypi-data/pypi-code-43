#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The nsh-item Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
hive datadownload

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/2/18
"""

from .impala_utils import ImpalaUtils


def datadownload(user_sql, conn_type='impala'):
    handler = ImpalaUtils(conn_type=conn_type)
    # USER_QUERY_SQL = open(sqlfile,'r',encoding='utf8').read()
    # user_sql = user_sql.replace('2019-01-01',ds)
    print('datadownload: ', user_sql)
    df = handler.exec_sql_query_pandas(sql=user_sql)
    handler.close_conn()
    return df
