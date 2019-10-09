#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 2019/7/22 0022 16:01 
# @Author : HL 
# @Site :  
# @File : Database1.py
# @Software: PyCharm
import pymysql


class Database2():
    host = '192.168.0.210'
    user = 'search_user'
    password = 'search_user'
    database = 'gmcms2_test'
    port = 3306
    charset = 'utf8'
    cursor = ''
    connet = ''

    def __init__(self):
        self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                      database=self.database,
                                      port=self.port, charset=self.charset)
        self.cursor = self.connet.cursor()

    def getCityCode(self, city):
        try:
            self.cursor.execute("select CODE,PROVINCEID from t_city where NAME = %s", city)
            result = self.cursor.fetchall()
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute("select CODE,PROVINCEID from t_city where NAME = %s", city)
            result = self.cursor.fetchall()
        return result

    def getProCode(self, code):
        try:
            self.cursor.execute("select PROVINCEID from t_city where CODE = %s", str(code))
            result = self.cursor.fetchall()
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute("select PROVINCEID from t_city where CODE = %s", str(code))
            result = self.cursor.fetchall()
        return result

    def getdistrictCode(self, city):
        try:
            self.cursor.execute("select CITYID,CODE from t_district where NAME = %s", city)
            result = self.cursor.fetchall()
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute("select CITYID,CODE from t_district where NAME = %s", city)
            result = self.cursor.fetchall()
        return result
