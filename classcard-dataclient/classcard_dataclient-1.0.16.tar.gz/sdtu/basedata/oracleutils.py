# -*- coding: utf-8 -*-
"""
Created By Murray(m18527) on 2019/9/10 11:21
"""
import os

import cx_Oracle as cx
from utils.loggerutils import logging
from config import ORACLE_SERVER

os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

logger = logging.getLogger(__name__)


def get_oracle_connection():
    conn = cx.connect(ORACLE_SERVER, encoding="UTF-8", nencoding="UTF-8")
    return conn


def upper(s):
    return str(s).upper()


def val_of(objs, idx):
    try:
        val = objs[idx]
    except:
        val = None
    return val


def alias_of(obj, k):
    try:
        val = obj[k]
    except:
        val = k
    return val


def select_data(sql):
    conn, cursor = None, None
    try:
        conn = get_oracle_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
    except Exception as e:
        logger.error("Error: exec select sql fail, Detail: {}".format(e))
        rows = []
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return rows


def deal_fields(fields):
    table_field = []
    alias_field = {}
    for f in fields:
        if isinstance(f, str):
            table_field.append(f)
        elif isinstance(f, (list, tuple)):
            field = val_of(f, 0)
            alias = val_of(f, 1)
            if field:
                table_field.append(field)
            if field and alias:
                alias_field[field] = alias
    return table_field, alias_field


def query_data(table_name, fields, params=None):
    """
    :param table_name:
    :param fields:
    :param params:  key=('=', 'val')
    :return:
    """
    if not fields or not table_name or not isinstance(fields, (list, tuple)):
        return {}
    table_name = upper(table_name)
    table_fields, alias_fields = deal_fields(fields)
    table_col_names = ",".join(table_fields)
    if params and isinstance(params, dict):
        query_params = " AND ".join(["{}{}'{}'".format(k, v[0], v[1]) for k, v in params.items()
                                     if k and isinstance(v, tuple)])
        q_sql = "SELECT {table_col_names} FROM {table_name} WHERE {query_params}".format(
            table_col_names=table_col_names, table_name=table_name, query_params=query_params)
    else:
        q_sql = "SELECT {table_col_names} FROM {table_name}".format(
            table_col_names=table_col_names, table_name=table_name)

    rows = select_data(q_sql)
    result = []
    for row in rows:
        row_data = {}
        for i in range(len(row)):
            field_name = val_of(table_fields, i)
            alias_field = alias_of(alias_fields, field_name)
            row_data[alias_field] = row[i]
        result.append(row_data)
    logger.info("SQL: {}, Number of rows returned: {}".format(q_sql, len(result)))
    return result
