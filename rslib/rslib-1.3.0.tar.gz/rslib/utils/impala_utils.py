#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2019 NetEase.com, Inc. All Rights Reserved.
# Copyright 2019, The nsh-item Recommendation Project, The User Persona Group, The Fuxi AI Lab.
"""
ImpalaUtils

Authors: wangkai02(wangkai02@corp.netease.com)
Phone: 17816029211
Date: 2019/2/18
"""

import os
import time
import datetime

import pandas as pd
from impala import dbapi

import sys
import importlib

importlib.reload(sys)
# https://stackoverflow.com/questions/961162/reloading-module-giving-nameerror-name-reload-is-not-defined

IMPALA_HOST_IP = 'fuxi-luoge-01'
IMPALA_HOST_PORT = 36001
IMPALA_DATABASE = "default"

HIVE_HOST_IP = 'fuxi-luoge-01'
HIVE_HOST_PORT = 36003
HIVE_DATABASE = "default"


class ImpalaUtils(object):
    def __init__(self, conn_type='impala'):
        if conn_type == 'hive':
            self.conn_type = 'hive'
            self.host = HIVE_HOST_IP
            self.port = HIVE_HOST_PORT
            self.db = HIVE_DATABASE
            self.conn = self.open_hive_conn()
        else:
            self.conn_type = 'impala'
            self.host = IMPALA_HOST_IP
            self.port = IMPALA_HOST_PORT
            self.db = IMPALA_DATABASE
            self.conn = self.open_impala_conn()

    def open_hive_conn(self):
        os.system('kinit -kt /home/fuxi/running/code/data/up_recommend.keytab up_recommend@FUXI-LUOGE-02')
        conn = dbapi.connect(host=self.host, port=self.port, database=self.db,
                             auth_mechanism='GSSAPI',
                             kerberos_service_name='hive')
        return conn

    def open_impala_conn(self):
        os.system('kinit -kt /home/fuxi/running/code/data/up_recommend.keytab up_recommend@FUXI-LUOGE-02')
        conn = dbapi.connect(host=self.host, port=self.port, database=self.db,
                             auth_mechanism='GSSAPI',
                             kerberos_service_name='impala')
        return conn

    def close_conn(self):
        self.conn.close()

    # Execute SELECT Statement
    # https://www.cloudera.com/documentation/enterprise/5-9-x/topics/impala_select.html#select
    def exec_sql_query(self, sql):
        # print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor

    # Execute DDL Statements
    # https://www.cloudera.com/documentation/enterprise/5-9-x/topics/impala_ddl.html#ddl
    def exec_sql_ddl(self, sql):
        # print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor

    # Execute DML Statements
    # https://www.cloudera.com/documentation/enterprise/5-9-x/topics/impala_dml.html#dml
    def exec_sql_dml(self, sql):
        # print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return True

    # Get SQL query result in pandas format
    def exec_sql_query_pandas(self, sql=None, param_list=None):
        # print(sql)
        with self.conn.cursor() as cursor:
            cursor.execute(sql, param_list)
            # print(cursor.description)
            if self.conn_type == 'hive':
                # HIVE连接拉取的数据表列名格式：table_name.column_name
                # fields = [x[0] for x in cursor.description]
                fields = [x[0].split('.')[1] for x in cursor.description]
                data = [dict(zip(fields, row)) for row in cursor]
                df = pd.DataFrame(data)
            else:
                from impala.util import as_pandas
                df = as_pandas(cursor)
                # IMPALA连接拉取的数据表列名格式：column_name
                # fields = [x[0] for x in cursor.description]
                # data = [dict(zip(fields, row)) for row in cursor]
                # df = pd.DataFrame(data)
            return df


# import impala.dbapi
# impala_ip = 'fuxi-luoge-01'
# impala_port = 36001
# def connect_impala(impala_ip, impala_port):
#     conn = impala.dbapi.connect(host=impala_ip, port=impala_port, auth_mechanism='GSSAPI',
#                                 kerberos_service_name='impala', database="default")
#     cursor = conn.cursor()
#     cursor.execute("show databases")
#     print(cursor.fetchall())
#     # cursor.execute('SELECT * FROM ball_ods.ods_addcrest LIMIT 10')
#     # print(cursor.description) # prints the result set's schema
#     # results = cursor.fetchall()
#     # print(results)
#     return cursor
# connect_impala(impala_ip, impala_port)


if __name__ == '__main__':
    handler = ImpalaUtils(conn_type='hive')

    sql = """
    SELECT * FROM luoge_nsh-item_ods.ods_nsh-item_matchinfo LIMIT 10
    """
    df = handler.exec_sql_query_pandas(sql=sql)
    # print(df)

    # df.fillna(0)
    # time.sleep(10)

    handler.close_conn()

    print('finish collecting data!')
