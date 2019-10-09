#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 2019/7/22 0022 11:21 
# @Author : HL 
# @Site :  
# @File : insertTagIC.py
# @Software: PyCharm
import os
import sys
from DatabaseMysql import Database

class inserTag():
    def __init__(self):
        self.db = Database()

    def insertToFirstTag(self, table):
        result = self.db.getFirstTag(table)
        for rlt in result:
            channel = rlt[0]
            # 先判断标签是否存在
            flag = self.db.is_exist_tag('1', channel)
            if flag:
                print('一级标签 ' + channel + ' 已存在！！！！')
                continue
            self.db.insertTags('1', channel, '0')
        print('一级标签 导入完毕！！！ 开始导入二级标签 ！！！')
        self.insertToSecondTag(table)

    def insertToSecondTag(self, table):
        result = self.db.getSecondTag(table)
        for rlt in result:
            types = rlt[0]
            channel = rlt[1]
            # 先判断标签是否存在
            flag = self.db.is_exist_tag('2', types)
            if flag:
                print('二级标签 ' + types + ' 已存在！！！！')
                continue
            parentId = self.db.getParentId(channel)
            self.db.insertTags('2', types, parentId[0])
        print('二级标签 导入完毕！！！')

if __name__ == '__main__':
    inserTag().insertToFirstTag('dianping_cities')
    inserTag().insertToFirstTag('dianpinga_cities')
    inserTag().insertToFirstTag('dianpingx_cities')
    inserTag().insertToFirstTag('dianpingz_cities')
    inserTag().insertToFirstTag('dianpingw_cities')
    inserTag().insertToFirstTag('dianpinglan_cities')
    inserTag().insertToFirstTag('dianpingp_cities')
    inserTag().insertToFirstTag('dianpingzhu_cities')
    inserTag().insertToFirstTag('dianpingm_cities')

    inserTag().insertToFirstTag('dianpingajk_cities')
    inserTag().insertToFirstTag('dianpingesf_cities_xiaoqu')
    inserTag().insertToFirstTag('dianpingxzl_cities')

    inserTag().insertToFirstTag('dianpingau_cities')
    inserTag().insertToFirstTag('gmcm_juooo')

