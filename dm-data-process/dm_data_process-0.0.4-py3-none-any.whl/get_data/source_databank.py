# coding: utf-8
"""
Created on 2018年5月28日

@author: Damon
"""
import pandas as pd
import pymssql
import pymysql
import cx_Oracle
from sqlalchemy import create_engine
import os
import psycopg2

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'


def read_pgsql(host, port, user, password, data_base, query):
    database = psycopg2.connect(host=host, user=user, password=password, database=data_base, port=port)
    cursor = database.cursor()
    data = pd.read_sql(query, database, )
    database.close()
    cursor.close()
    return data


def insert_pgsql(host, port, user, password, data_base, data, table_name):
    database = create_engine('postgresql://' + user + ':' + password + '@' + host + ':' + str(
        port) + '/' + data_base)
    data.to_sql(table_name, con=database, index=False, if_exists='append', chunksize=10000)


def execute_pgsql(host, port, user, password, data_base, query):
    database = psycopg2.connect(host=host, user=user, password=password, database=data_base, port=port)
    cursor = database.cursor()
    cursor.execute(query)
    database.commit()
    cursor.close()
    database.close()


# 连接mysql
def read_mysql(host, port, user, password, data_base, query):
    database = pymysql.connect(host=host, user=user, password=password, database=data_base, port=port, charset='utf8')
    cursor = database.cursor()
    data = pd.read_sql(query, database, )
    database.close()
    cursor.close()
    return data


def insert_mysql(host, port, user, password, data_base, data, table_name):
    database = create_engine('mysql+pymysql://' + user + ':' + password + '@' + host + ':' + str(
        port) + '/' + data_base + '?charset=utf8mb4')
    data.to_sql(table_name, con=database, index=False, if_exists='append', chunksize=10000)


def execute_mysql(host, port, user, password, data_base, query):
    database = pymysql.connect(host=host, user=user, password=password, db=data_base, port=port, charset='utf8mb4')
    cursor = database.cursor()
    cursor.execute(query)
    database.commit()
    cursor.close()
    database.close()


# 连接oracle
def read_oracle(host, user, password, service, query):
    database = cx_Oracle.connect(user + '/' + password + '@' + host + '/' + service)
    cursor = database.cursor()
    data = pd.read_sql(query, database, )
    database.close()
    cursor.close()
    return data


def insert_oracle(host, user, password, service, data, table_name):
    database = create_engine('oracle://' + user + ':' + password + '@' + host + '/' + service)
    data.to_sql(table_name, con=database, index=False, if_exists='append', chunksize=10000)


def execute_oracle(host, user, password, service, query):
    database = cx_Oracle.connect(user + '/' + password + '@' + host + '/' + service)
    cursor = database.cursor()
    cursor.execute(query)
    database.commit()
    cursor.close()
    database.close()


# 连接sqlserver
def read_sqlserver(host, user, password, data_base, query):
    database = pymssql.connect(host=host, user=user, password=password, database=data_base, charset='utf8')
    cursor = database.cursor()
    data = pd.read_sql(query, database, )
    database.close()
    cursor.close()
    return data


def insert_sqlserver(host, user, password, data_base, data, table_name):
    database = create_engine(
        'mssql+pymssql://' + user + ':' + password + '@' + host + '/' + data_base + '?charset=utf8')
    data.to_sql(table_name, con=database, index=False, if_exists='append', chunksize=10000)


def execute_sqlserver(host, user, password, data_base, query):
    database = pymssql.connect(host=host, user=user, password=password, database=data_base)
    cursor = database.cursor()
    cursor.execute(query)
    database.commit()
    cursor.close()
    database.close()
