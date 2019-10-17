# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
import math
import pymysql.cursors


class MysqlCli:
    def __init__(self, host, user, password, db, port=3306):
        """
        create connection to mysql
        """
        try:
            self.db_info = pymysql.connect(host=host,
                                           user=user,
                                           passwd=password,
                                           db=db,
                                           port=port,
                                           charset="utf8")
        except Exception as e:
            raise e

    def query_mysql(self, sql):
        """
        query
        """
        with self.db_info.cursor() as cursor:
            cursor.execute(sql)
            self.db_info.commit()
            return cursor.fetchall()

    def query_part_mysql(self, sql, max=-1, Len=10000):
        """
        query
        """
        id, fetch = 0, 1
        query_out = tuple()
        if max >= 0:
            with self.db_info.cursor() as cursor:
                while fetch and id < max:
                    cursor.execute("{} limit {},{}".format(sql, id, Len))
                    self.db_info.commit()
                    fetch = cursor.fetchall()
                    id += Len
                    if fetch:
                        query_out += fetch
        else:
            with self.db_info.cursor() as cursor:
                while fetch:
                    cursor.execute("{} limit {},{}".format(sql, id, Len))
                    self.db_info.commit()
                    fetch = cursor.fetchall()
                    id += Len
                    if fetch:
                        query_out += fetch
        return query_out

    def execute_mysql(self, sql):
        """
        query
        """
        with self.db_info.cursor() as cursor:
            cursor.execute(sql)
            self.db_info.commit()

    def execute_many(self, sql, args):
        """
        executemany
        """
        with self.db_info.cursor() as cursor:
            cursor.executemany(sql, args)
            self.db_info.commit()

    def cursor_mysql(self):
        return self.db_info.cursor()

    def ping_mysql(self):
        self.db_info.ping(True)

    def commit(self):
        self.db_info.commit()

    def rollback(self):
        self.db_info.rollback()

    def update_data_by_insert(self, features: dict, key: str, field: str, table: str, times=1000):
        """
        update_data_by_insert: insert data on  DUPLICATE key 字段更新
        :param features: data
        :param key: 主键
        :param field: 更新字段
        :param table: 表名
        :param times: 次数
        :return:
        """
        if len(features) < 1:
            return

        feature_list = [[k, v] for k, v in features.items()]
        try:
            L = int(math.ceil(len(features) / times))
            for d in [feature_list[i:i + L] for i in range(0, len(feature_list), L)]:
                sql = """
                INSERT INTO 
                `{t}` (`{k}`,`{f}`) 
                VALUES {d} on DUPLICATE key 
                update `{f}`=values(`{f}`);
                """.format(t=table,
                           d=','.join(["('{}','{}')".format(x[0], x[1]) for x in d]),
                           k=key,
                           f=field)
                self.execute_mysql(sql)
        except Exception as e:
            self.db_info.rollback()
            raise e

    def update_data_by_replace(self, features: list, table: str, *keys, times=100):
        """
        整表replace更新
        :param features:
        :param key:
        :param field:
        :param table:
        :param times:
        :return:
        """
        if len(features) < 1:
            return

        try:
            L = int(math.ceil(len(features) / times))
            for d in [features[i:i + L] for i in range(0, len(features), L)]:
                sql = """
                REPLACE INTO 
                `{t}` ({k}) 
                VALUES {d};
                """.format(t=table,
                           d=','.join(["(" + ",".join(["'" + str(x) + "'" for x in dl]) + ")" for dl in d]),
                           k=','.join(keys))
                self.execute_mysql(sql)
        except Exception as e:
            self.db_info.rollback()
            raise e

    def close_mysql(self):
        """
        close connection
        """
        self.db_info.close()
