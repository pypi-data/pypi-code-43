#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The nsh-item Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
exec_hive

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/2/18
"""

from .impala_utils import ImpalaUtils


def exec_hive(sqlfiles, ds, conn_type='impala'):
    handler = ImpalaUtils(conn_type)
    for sqlfile in sqlfiles:
        USER_QUERY_SQL = open(sqlfile, 'r', encoding='utf8').read()
        user_sql = USER_QUERY_SQL.replace('2019-04-01', ds)
        print('exec_sql: ', user_sql)
        df = handler.exec_sql_dml(sql=user_sql)
    handler.close_conn()
