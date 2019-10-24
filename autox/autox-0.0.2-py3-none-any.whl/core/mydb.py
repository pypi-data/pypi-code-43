#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 基础包：数据库

import pymysql.cursors
import autox.core.mylog as log

logging = log.track_log()


def connect(host, user, password, db, charset='utf8'):
    """
    连接MySQL
    :param host: 数据库主机
    :param user: 用户名
    :param password: 密码
    :param db: 库名
    :return: 连接
    """

    # if con is None:
    con = pymysql.connect(host=host, user=user, password=password, db=db, charset=charset, cursorclass=pymysql.cursors.DictCursor)
        # cursorclass=pymysql.cursors.DictCursor
    return con


def execute(con, sql):
    """
    执行SQL
    :param sql: sql语句
    :return: 执行结果
    """
    try:
        cursor = con.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        con.commit()
        return result

    except Exception as e:
        logging.error("执行sql失败:%s" % (e.__repr__()))
        con.rollback()
    con.close()


def close(con):
    """关闭MySQL"""
    con.close()



