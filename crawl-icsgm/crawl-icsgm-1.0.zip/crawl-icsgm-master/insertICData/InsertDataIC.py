#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 2019/7/22 0022 9:50 
# @Author : HL 
# @Site :  
# @File : InsertDataSY.py
# @Software: PyCharm
from DatabaseMysql import Database
from Database import Database2
import cityList


class inserDataIC():
    def __init__(self):
        self.db = Database()
        self.db2 = Database2()

    def getMessage(self, table, startTime, endTime):
        result = self.db.getDataFromTableIC(table, startTime, endTime)
        return result

    def process(self, result, creatTime):
        if '.' in creatTime:
            splt = creatTime.split('.')
            times = splt[0] + '-' + splt[1] + '-01 00:00:00'
        else:
            splt = creatTime.split('-')
            times = splt[0] + '-' + splt[1] + '-01 00:00:00'
        for rlt in result:
            source = rlt[0]
            count = rlt[1]
            mediaIds = self.db.getMeidaId(source)
            self.db.saveCarLifeIC(mediaIds[0], count, '1', times)
            print('导入一条数据！数据是：' + source + ' ' + str(
                count))

    def insertToTable(self, table, startTime, endTime):
        result = self.getMessage(table, startTime, endTime)
        self.process(result, startTime)


if __name__ == '__main__':
    s = '07'
    ss = '08'
    inserDataIC().insertToTable('t_original_crawl', '2019-' + s + '-01 00:00:00', '2019-' + ss + '-01 00:00:00')
    inserDataIC().insertToTable('t_product_craw_competitor', '2019-' + s + '-01 00:00:00',
                                '2019-' + ss + '-01 00:00:00')
