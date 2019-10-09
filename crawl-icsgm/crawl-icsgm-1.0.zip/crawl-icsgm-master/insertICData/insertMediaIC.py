#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 2019/7/22 0022 15:15 
# @Author : HL 
# @Site :  
# @File : insertMediaSY.py
# @Software: PyCharm
from DatabaseMysql import Database

class insertMediaIC():
    def __init__(self):
        self.db = Database()

    def insertmedia(self, table):
        result = self.db.getMeidaIC(table)
        for rlt in result:
            meida = rlt[0]
            # 先判断标签是否存在
            flag = self.db.is_exist_media(meida)
            if flag:
                print('媒体 ' + meida + ' 已存在！！！！')
                continue
            self.db.insertMedia(meida)
        print('媒体 导入完毕！！！ ！！！')


if __name__ == '__main__':
    insertMediaIC().insertmedia('t_original_crawl')
    insertMediaIC().insertmedia('t_product_craw_competitor')

