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


class inserData():
    def __init__(self):
        self.db = Database()
        self.db2 = Database2()

    def getMessage(self, table, startTime, endTime):
        result = self.db.getDataFromTable(table, startTime, endTime)
        return result

    def process(self, result, creatTime):
        if '.' in creatTime:
            splt = creatTime.split('.')
            times = splt[0] + '-' + splt[1] + '-01 00:00:00'
        else:
            splt = creatTime.split('-')
            times = splt[0] + '-' + splt[1] + '-01 00:00:00'
        for rlt in result:
            province = rlt[0]
            city = rlt[1]
            channel = rlt[2]
            type = rlt[3]
            source = rlt[4]
            count = rlt[5]
            # crawl_time = rlt[]
            clst = cityList.cityList()
            if city in clst:
                codes = clst[city]
                splt = codes.split(',')
                cityCode = splt[0]
                proCode = splt[1]
                # codes = self.db2.getCityCode(city)
                # if len(codes) == 0:
                #     codes = self.db2.getCityCode(city + '市')
                #     if len(codes) == 0:
                #         print(city + ' 没有搜索到城市表ID！！！！')
                #         continue
                # cityCode = codes[0][0]
                # proCode = codes[0][1]
                mediaIds = self.db.getMeidaId(source)
                channelId = self.db.getTagId(channel, '1')
                typeId = self.db.getTagId(type, '2')
                self.db.saveCarLife(mediaIds[0], proCode, cityCode, channelId[0], typeId[0], count, '1', times)
                print('导入一条数据！数据是：' + city + ' ' + type + ' ' + source + ' ' + str(
                    count))
            else:
                print('城市表中没有 ' + city + ' ！！！！！')

    def insertToTable(self, table, startTime, endTime):
        result = self.getMessage(table, startTime, endTime)
        self.process(result, startTime)


if __name__ == '__main__':
    s = '09'
    ss = '10'
    inserData().insertToTable('dianping_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    inserData().insertToTable('dianpinga_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    inserData().insertToTable('dianpingx_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    inserData().insertToTable('dianpingau_cities', '2019-' + s + '-01 00:00:00', '2019-' + ss + '-01 00:00:00')

    inserData().insertToTable('dianpingz_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    inserData().insertToTable('dianpingw_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    inserData().insertToTable('dianpinglan_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    inserData().insertToTable('dianpingp_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    inserData().insertToTable('dianpingzhu_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    inserData().insertToTable('dianpingm_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    #
    inserData().insertToTable('dianpingajk_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    inserData().insertToTable('dianpingesf_cities_xiaoqu', '2019.' + s + '.01', '2019.' + ss + '.01')
    inserData().insertToTable('dianpingxzl_cities', '2019.' + s + '.01', '2019.' + ss + '.01')
    #

    # lst = ['11', '10', '9', '8']
    # for n in lst:
    #     print('=================== ' + n)
    #     m = str(int(n) + 1)
    #     inserData().insertToTable('dianping_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #     inserData().insertToTable('dianpinga_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #     inserData().insertToTable('dianpingx_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #     inserData().insertToTable('dianpingz_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #     inserData().insertToTable('dianpingw_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #     inserData().insertToTable('dianpinglan_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #     inserData().insertToTable('dianpingp_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #     inserData().insertToTable('dianpingzhu_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #     inserData().insertToTable('dianpingm_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #
    #     inserData().insertToTable('dianpingajk_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #     inserData().insertToTable('dianpingesf_cities_xiaoqu', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #     inserData().insertToTable('dianpingxzl_cities', '2018.0' + n + '.01', '2018.0' + m + '.01')
    #
    #     inserData().insertToTable('dianpingau_cities', '2018-0' + n + '-01 00:00:00', '2018-0' + m + '-01 00:00:00')
    #
    #     inserData().insertToTable('gmcm_juooo', '2018.0' + n + '.01', '2018.0' + m + '.01')
