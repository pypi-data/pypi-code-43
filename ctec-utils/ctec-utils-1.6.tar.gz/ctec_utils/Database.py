# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Wjy
import cx_Oracle
import pymysql
from DBUtils.PooledDB import PooledDB
from rediscluster import StrictRedisCluster
from pymongo import MongoClient


class OraclePool(object):
    """
    封装cx_oracle，创建连接池对象

    示例：
        oracle = OraclePool(用户名, 密码, 'ip/库' 或 dsn, 最小连接数, 最大连接数)
    """

    def __init__(self, user: str, password: str, dsn: str, mincached: int, maxcached: int,
                 maxconnections=10, threaded: bool = False, **kwargs):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.min_cached = mincached
        self.max_cached = maxcached
        self.maxconnections = maxconnections
        self.threaded = threaded
        self.kwargs = kwargs
        self._connection = self.__get_connect()

    def __get_connect(self):
        # 创建连接对象
        return PooledDB(cx_Oracle,
                        user=self.user,
                        password=self.password,
                        dsn=self.dsn,
                        mincached=self.min_cached,
                        maxcached=self.max_cached,
                        maxconnections=self.maxconnections,
                        threaded=self.threaded, **self.kwargs)

    @staticmethod
    def give_back(conn, cursor):
        try:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
        except Exception as e:
            pass

    def procedure_cursor(self, procedure_name: str, *args, commit: bool = False):
        """
        存储过程返回游标对象
        :param procedure_name: 存过名
        :param args: 入参
        :param commit: 是否commit
        :return:
        """
        conn, cursor = None, None
        return_list = []
        try:
            conn = self._connection.connection()
            cursor = conn.cursor()
            result = cursor.var(cx_Oracle.CURSOR)
            params = list(args)
            params.append(result)
            _, resp_result = cursor.callproc(procedure_name, params)
            if commit:
                conn.commit()
        except Exception as e:
            if conn:
                self.rollback(conn)
            return None
        else:
            for res in list(result.getvalue()):
                return_list.append(dict(zip([resp[0] for resp in resp_result.description], res)))
            return return_list

    def procedure_string(self, procedure_name: str, *args, commit: bool = False):
        """
        存储过程返回值
        :param procedure_name: 存过名
        :param args: 入参
        :param commit: 是否commit
        :return:
        """
        conn, cursor = None, None
        try:
            conn = self._connection.connection()
            cursor = conn.cursor()
            result = cursor.var(cx_Oracle.STRING)
            params = list(args)
            params.append(result)
            cursor.callproc(procedure_name, params)
            if commit:
                conn.commit()
        except Exception as e:
            if conn:
                self.rollback(conn)
            return None
        else:
            return result.getvalue()

    def row_sql(self, sql: str, param: dict):
        """
        原生sql

        例如：
            o = OraclePool("user", "password", 'dsn', 0, 1)
            print(o.row_sql("select * from 表 where ROWNUM < :num", {"num": 10}))
        :param sql: sql语句
        :param param: 入参
        :return:
        """
        try:
            conn = self._connection.connection()
            cursor = conn.cursor()
            cursor.prepare(sql)
            cursor.execute(None, param)
            result = cursor.fetchall()

            if isinstance(result, list) and len(result) > 0:
                return_result = list()
                key_list = [key[0] for key in cursor.description]
                for value in result:
                    return_result.append(dict(zip(key_list, value)))
                self.give_back(conn, cursor)
                return return_result
            self.give_back(conn, cursor)
            return result
        except Exception as e:
            raise e

    def row_sql_commit(self, sql: str, param: dict):
        """
        原生sql

        例如：
            o = OraclePool("user", "password", 'dsn', 0, 1)
            print(o.row_sql("select * from 表 where ROWNUM < :num", {"num": 10}))
        :param sql: sql语句
        :param param: 入参
        :return:
        """
        conn, cursor = None, None
        try:
            conn = self._connection.connection()
            cursor = conn.cursor()
            cursor.prepare(sql)
            cursor.execute(None, param)
            result = cursor.rowcount
            conn.commit()
            self.give_back(conn, cursor)
            return result
        except Exception as e:
            self.rollback(conn)
            self.give_back(conn, cursor)
            raise e

    def row_sql_list(self, sql_list: list):
        """
        多sql提交
        :param sql_list: {"sql": "UPDATE 表 SET ORDER_STATUS = :order_status WHERE ORDER_ID = :order_id",
             "params": {"order_id": "1234567", "order_status": "Z0101"}},
            {
                "sql": "insert into 表1(ID, BUSINESS_ID, ORDER_ID) values(:id, :business_id, :order_id)",
                "params": {"id": "555555", "business_id": "6666666", "order_id": "7777777"}
            }
        :return:
        """
        conn, cursor = None, None
        try:
            conn = self._connection.connection()
            row_counts = list()
            for sql in sql_list:
                cursor = conn.cursor()
                cursor.prepare(sql["sql"])
                cursor.execute(None, sql["params"])
                count = cursor.rowcount
                row_counts.append(count)
            conn.commit()
            self.give_back(conn, cursor)
            return row_counts
        except Exception as e:
            self.rollback(conn)
            self.give_back(conn, cursor)
            raise e

    def rollback(self, conn):
        try:
            conn.rollback()
        except:
            pass


class RowOraclePool(object):

    def __init__(self, user: str, password: str, dsn: str, mincached: int, maxcached: int, threaded: bool = False, **kwargs):
        self.user = user
        self.password = password
        self.dsn = dsn
        self.min_cached = mincached
        self.max_cached = maxcached
        self.threaded = threaded
        self.kwargs = kwargs
        self._connection = self.__get_connect()

    def __get_connect(self):
        # 创建连接对象
        return cx_Oracle.SessionPool(
                        user=self.user,
                        password=self.password,
                        dsn=self.dsn,
                        min=self.min_cached,
                        max=self.max_cached,
                        threaded=self.threaded, **self.kwargs)

    def row_sql(self, sql: str, param: dict):
        """
        原生sql

        例如：
            o = OraclePool("user", "password", 'dsn', 0, 1)
            print(o.row_sql("select * from 表 where ROWNUM < :num", {"num": 10}))
        :param sql: sql语句
        :param param: 入参
        :param commit: 是否commit
        :return:
        """
        conn = None
        try:
            conn = self._connection.acquire()
            cursor = conn.cursor()
            cursor.execute(sql, param)
            result = cursor.fetchall()
        except Exception as e:
            self.rollback(conn)
            self._connection.release(conn)
            raise e
        else:
            if isinstance(result, list) and len(result) > 0:
                return_result = list()
                key_list = [key[0] for key in cursor.description]
                for value in result:
                    return_result.append(dict(zip(key_list, value)))
                self._connection.release(conn)
                return return_result
            self._connection.release(conn)
            return result

    def row_sql_commit(self, sql: str, param: dict):
        """
        原生sql

        例如：
            o = OraclePool("user", "password", 'dsn', 0, 1)
            print(o.row_sql("select * from 表 where ROWNUM < :num", {"num": 10}))
        :param sql: sql语句
        :param param: 入参
        :param commit: 是否commit
        :return:
        """
        conn = None
        try:
            conn = self._connection.acquire()
            cursor = conn.cursor()
            cursor.execute(sql, param)

            result = cursor.rowcount
            conn.commit()
        except Exception as e:
            self.rollback(conn)
            raise e
        else:
            self._connection.release(conn)
            return result

    def row_sql_list(self, sql_list: list):
        """
        多sql提交
        :param sql_list: {"sql": "UPDATE 表 SET ORDER_STATUS = :order_status WHERE ORDER_ID = :order_id",
             "params": {"order_id": "1234567", "order_status": "Z0101"}},
            {
                "sql": "insert into 表1(ID, BUSINESS_ID, ORDER_ID) values(:id, :business_id, :order_id)",
                "params": {"id": "555555", "business_id": "6666666", "order_id": "7777777"}
            }
        :return:
        """
        conn = None
        try:
            conn = self._connection.acquire()
            row_counts = list()
            for sql in sql_list:
                cursor = conn.cursor()
                cursor.execute(sql["sql"], sql["params"])
                count = cursor.rowcount
                row_counts.append(count)
            conn.commit()
            self._connection.release(conn)
            return row_counts
        except Exception as e:
            if conn:
                self.rollback(conn)
            raise e

    def reload(self):
        try:
            # 释放池
            self._connection.release()
        except:
            pass
        self._connection = self.__get_connect()

    def rollback(self, conn):
        try:
            conn.rollback()
        except:
            pass


class RedisCluster(object):
    """
    连接redis集群

    示例：
        redis_nodes = [
            {'host': 'host', 'port': port},
            {'host': 'host', 'port': port},
        ]

        redis = RedisCluster(redis_nodes)
        conn = redis.conn
        conn.get("键")
    """

    def __init__(self, redis_nodes: list, **kwargs):
        self.redis_nodes = redis_nodes
        self.kwargs = kwargs
        self.conn = self.get_conn()

    def get_conn(self):
        return StrictRedisCluster(startup_nodes=self.redis_nodes, **self.kwargs)


class MongodbCluster(object):
    """
    连接mongodb集群

    示例：
        mongodb_nodes = [
             {'host': 'host', 'port': port},
             {'host': 'host', 'port': port},
        ]

        mongodb = Mongodb("user", "password", mongodb_nodes, **kwargs)
        mongodb.conn
    """

    def __init__(self, user: str = "", password: str = "", hosts: list = None, **kwargs):
        self.user = user
        self.password = password
        self.kwargs = kwargs
        self.conn = self.get_connect(hosts)

    def get_connect(self, hosts):
        db = self.kwargs.pop("db")
        if self.user:
            hosts_list = ",".join(["{}:{}".format(host["host"], host["port"]) for host in hosts])
            url = "mongodb://{user}:{password}@{list}/".format(user=self.user, password=self.password, list=hosts_list)
            if db:
                url += db
            return MongoClient(url)
        else:
            hosts_list = ",".join(["{}:{}".format(host["host"], host["port"]) for host in hosts])
            url = "mongodb://{list}/".format(list=hosts_list)
            if db:
                url += db
            return MongoClient(url, **self.kwargs)


class MysqlPool(object):
    """
    未测试mysql连接池

    示例：

        mysql = MysqlPool(host=host, port=3306, user="root", password="mysql", mincached=0, maxcached=1, db=库名)
        print(mysql.row_sql("show databases;"))
    """
    def __init__(self, user: str, password: str, host: str, port: int, mincached: int, maxcached: int,
                 db: str, **kwargs):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.db = db
        self.min_cached = mincached
        self.max_cached = maxcached
        self.kwargs = kwargs
        self._connection = self.__get_connect()

    def __get_connect(self):
        # setsession=['SET AUTOCOMMIT = 1']是用来设置线程池是否打开自动更新的配置，0为False，1为True
        return PooledDB(pymysql,
                        host=self.host,
                        user=self.user,
                        passwd=self.password,
                        db=self.db,
                        port=self.port,
                        mincached=self.min_cached,
                        maxcached=self.max_cached, **self.kwargs)

    def row_sql(self, sql, param=None, commit=False):
        """
        暂时只提供原生sql
        :param sql: sql语句
        :param param: 参数
        :param commit: 是否commit
        :return:
        """
        conn = None
        try:
            conn = self._connection.connection()  # 以后每次需要数据库连接就是用connection（）函数获取连接就好了
            cur = conn.cursor(pymysql.cursors.DictCursor)
            result = cur.execute(sql, param)
            if commit:
                results = result.rowcount
                if result is 0:
                    self.rollback(conn)
                else:
                    conn.commit()
            else:
                results = cur.fetchall()
            conn.close()
        except Exception as e:
            if conn:
                self.rollback(conn)
            raise e
        else:
            return results

    def row_sql_list(self, sql_list: list):
        """
        多sql提交
        :param sql_list: {"sql": "UPDATE 表 SET ORDER_STATUS = :order_status WHERE ORDER_ID = :order_id",
             "params": {"order_id": "1234567", "order_status": "Z0101"}},
            {
                "sql": "insert into 表1(ID, BUSINESS_ID, ORDER_ID) values(:id, :business_id, :order_id)",
                "params": {"id": "555555", "business_id": "6666666", "order_id": "7777777"}
            }
        :return:
        """
        conn = None
        try:
            conn = self._connection.connection()
            cursor = conn.cursor()
            row_counts = list()
            for sql in sql_list:
                cursor.execute(sql["sql"], sql["params"])
                count = cursor.rowcount
                if count is 0:
                    self.rollback(conn)
                    return None
                row_counts.append(count)
            conn.commit()
            return row_counts
        except Exception as e:
            if conn:
                self.rollback(conn)
            raise e

    def rollback(self, conn):
        """
        尝试回滚
        :param conn:
        :return:
        """
        try:
            conn.rollback()
        except:
            pass
