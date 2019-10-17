# !/usr/bin/python
# -*- coding: UTF-8 -*-
"""
Created on MAY 21, 2018
@author: zlh
hive client
"""
from pyhive import hive


class HiveCli:
    def __init__(self, host, db, port=10000, authMechanism="KERBEROS"):
        """
        create connection to hive server2
        """
        try:
            self.conn = hive.connect(host=host,
                                     port=port,
                                     auth=authMechanism,
                                     kerberos_service_name="hive",
                                     database=db)
        except Exception as e:
            raise e

    def query_hive(self, sql):
        """
        query
        """
        with self.conn.cursor() as cursor:
            cursor.execute(sql)
            return cursor.fetchall()

    def close_hive(self):
        """
        close connection
        """
        self.conn.close()
