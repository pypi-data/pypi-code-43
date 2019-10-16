# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
"""
from pyutils.yamls import read_from_yaml
import pymssql


class SqlserverCli:
    def __init__(self, host, user, password, db, port=3306):
        """
        create connection to mssql
        """
        try:
            self.db = pymssql.connect(host=host,
                                      user=user,
                                      password=password,
                                      database=db,
                                      port=port,
                                      charset="utf8")
        except Exception as e:
            raise e

    def query_mssql(self, sql):
        """
        query
        """
        with self.db.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def close_mssql(self):
        """
        close connection
        """
        self.db.close()
