#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 2019/7/22 0022 15:15 
# @Author : HL 
# @Site :  
# @File : insertMediaSY.py
# @Software: PyCharm
from DatabaseMysql import Database


class insertMedia():
    def __init__(self):
        self.db = Database()

    def insertmedia(self, table):
        result = self.db.getMeida(table)
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
    insertMedia().insertmedia('dianping_cities')
    insertMedia().insertmedia('dianpinga_cities')
    insertMedia().insertmedia('dianpingx_cities')
    insertMedia().insertmedia('dianpingz_cities')
    insertMedia().insertmedia('dianpingw_cities')
    insertMedia().insertmedia('dianpinglan_cities')
    insertMedia().insertmedia('dianpingp_cities')
    insertMedia().insertmedia('dianpingzhu_cities')
    insertMedia().insertmedia('dianpingm_cities')

    insertMedia().insertmedia('dianpingajk_cities')
    insertMedia().insertmedia('dianpingesf_cities_xiaoqu')
    insertMedia().insertmedia('dianpingxzl_cities')

    insertMedia().insertmedia('dianpingau_cities')

    insertMedia().insertmedia('gmcm_juooo')

