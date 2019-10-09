#!/usr/bin/env python 
# -*- coding: utf-8 -*- 
# @Time : 2019/7/22 0022 9:51 
# @Author : HL 
# @Site :  
# @File : DatabaseMysql.py
# @Software: PyCharm
import time

import pymysql


class Database():
    host = '192.168.0.210'
    user = 'search_user'
    password = 'search_user'
    database = 'gmcms2_test'
    port = 3306
    charset = 'utf8'
    cursor = ''
    connet = ''

    # host2 = '127.0.0.1'
    # user2 = 'root'
    # password2 = 'root1226'
    # database2 = 'yappam'
    # cursor2 = ''
    # connet2 = ''

    host2 = '192.168.0.210'
    user2 = 'search_user'
    password2 = 'search_user'
    database2 = 'gmcms2_dev_statistic'
    cursor2 = ''
    connet2 = ''

    def __init__(self):
        self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password, database=self.database,
                                      port=self.port, charset=self.charset)
        self.cursor = self.connet.cursor()
        self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                       database=self.database2,
                                       port=self.port, charset=self.charset)
        self.cursor2 = self.connet2.cursor()

    def getDataFromTable(self, table, startTime, endTime):
        try:
            self.cursor2.execute(
                "select province,city,channel,type,source,count(0) as count from " + table + " where crawl_time >= '" + startTime + "' and crawl_time < '" + endTime + "' GROUP BY province,city,channel,type,source order by count desc")
            result = self.cursor2.fetchall()
        except Exception as info:
            print(info)
            self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                           database=self.database2,
                                           port=self.port, charset=self.charset)
            self.cursor2 = self.connet2.cursor()
            self.cursor2.execute(
                "select province,city,channel,type,source,count(0) as count from " + table + " where crawl_time > '" + startTime + "' and crawl_time < '" + endTime + "' GROUP BY province,city,channel,type,source order by count desc")
            result = self.cursor2.fetchall()
        return result
    def getDataFromTableSH(self, table, startTime, endTime):
        try:
            self.cursor2.execute(
                "select channel,type,count(0) as count from " + table + " where crawl_time >= '" + startTime + "' and crawl_time < '" + endTime + "' GROUP BY channel,type order by count desc")
            result = self.cursor2.fetchall()
        except Exception as info:
            print(info)
            self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                           database=self.database2,
                                           port=self.port, charset=self.charset)
            self.cursor2 = self.connet2.cursor()
            self.cursor2.execute(
                "select channel,type,count(0) as count from " + table + " where crawl_time >= '" + startTime + "' and crawl_time < '" + endTime + "' GROUP BY channel,type order by count desc")
            result = self.cursor2.fetchall()
        return result

    def getDataFromTableIC(self, table, startTime, endTime):
        try:
            self.cursor2.execute(
                "select source_site,count(0) as count from " + table + " where cdate >= '" + startTime + "' and cdate < '" + endTime + "' GROUP BY source_site order by count desc")
            result = self.cursor2.fetchall()
        except Exception as info:
            print(info)
            self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                           database=self.database2,
                                           port=self.port, charset=self.charset)
            self.cursor2 = self.connet2.cursor()
            self.cursor2.execute(
                "select source_site,count(0) as count from " + table + " where cdate >= '" + startTime + "' and cdate < '" + endTime + "' GROUP BY source_site order by count desc")
            result = self.cursor2.fetchall()
        return result

    def getDataFromTableSY(self, table, startTime, endTime):
        try:
            self.cursor2.execute(
                "select source,count(0) as count from " + table + " where publish_time >= '" + startTime + "' and publish_time < '" + endTime + "' GROUP BY source order by count desc")
            result = self.cursor2.fetchall()
        except Exception as info:
            print(info)
            self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                           database=self.database2,
                                           port=self.port, charset=self.charset)
            self.cursor2 = self.connet2.cursor()
            self.cursor2.execute(
                "select source,count(0) as count from " + table + " where publish_time >= '" + startTime + "' and publish_time < '" + endTime + "' GROUP BY source order by count desc")
            result = self.cursor2.fetchall()
        return result

    def getDataFromTableNoCity(self, table, startTime, endTime):
        try:
            self.cursor2.execute(
                "select city,channel,type,source,count(0) as count from " + table + " where crawl_time >= '" + startTime + "' and crawl_time < '" + endTime + "' GROUP BY city,channel,type,source order by count desc")
            result = self.cursor2.fetchall()
        except Exception as info:
            print(info)
            self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                           database=self.database2,
                                           port=self.port, charset=self.charset)
            self.cursor2 = self.connet2.cursor()
            self.cursor2.execute(
                "select province,city,channel,type,source,count(0) as count from " + table + " where crawl_time > '" + startTime + "' and crawl_time < '" + endTime + "' GROUP BY province,city,channel,type,source order by count desc")
            result = self.cursor2.fetchall()
        return result

    def getCitys(self):
        try:
            self.cursor2.execute("select cityName from dianping_cities_num")
            result = self.cursor2.fetchall()
        except Exception as info:
            print(info)
            self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                           database=self.database2,
                                           port=self.port, charset=self.charset)
            self.cursor2 = self.connet2.cursor()
            self.cursor2.execute("select cityName from dianping_cities_num")
            result = self.cursor2.fetchall()
        return result

    def getParentId(self, channel):
        try:
            self.cursor.execute("select id from t_carLife_tag where TAG_NAME = %s", channel)
            result = self.cursor.fetchall()
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute("select id from t_carLife_tag where TAG_NAME = %s", channel)
            result = self.cursor.fetchall()
        return result

    def getFirstTag(self, table):
        try:
            self.cursor2.execute("select channel from " + table + " group by channel")
            result = self.cursor2.fetchall()
        except Exception as info:
            print(info)
            self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                           database=self.database2,
                                           port=self.port, charset=self.charset)
            self.cursor2 = self.connet2.cursor()
            self.cursor2.execute("select channel from " + table + " group by channel")
            result = self.cursor2.fetchall()
        return result

    def getTagId(self, tag, level):
        try:
            self.cursor.execute("select id from t_carLife_tag where TAG_NAME = %s and TAG_LEVEL = %s",
                                (tag, str(level)))
            result = self.cursor.fetchall()
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute("select id from t_carLife_tag where TAG_NAME = %s and TAG_LEVEL = %s",
                                (tag, str(level)))
            result = self.cursor.fetchall()
        return result

    def getMeida(self, table):
        try:
            self.cursor2.execute("select source from " + table + " group by source")
            result = self.cursor2.fetchall()
        except Exception as info:
            print(info)
            self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                           database=self.database2,
                                           port=self.port, charset=self.charset)
            self.cursor2 = self.connet2.cursor()
            self.cursor2.execute("select source from " + table + " group by source")
            result = self.cursor2.fetchall()
        return result

    def getMeidaIC(self, table):
        try:
            self.cursor2.execute("select source_site from " + table + " group by source_site")
            result = self.cursor2.fetchall()
        except Exception as info:
            print(info)
            self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                           database=self.database2,
                                           port=self.port, charset=self.charset)
            self.cursor2 = self.connet2.cursor()
            self.cursor2.execute("select source from " + table + " group by source")
            result = self.cursor2.fetchall()
        return result

    def getMeidaId(self, media):
        try:
            self.cursor.execute("select id from t_carLife_media where media_name = %s", media)
            result = self.cursor.fetchall()
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute("select id from t_carLife_media where media_name = %s", media)
            result = self.cursor.fetchall()
        return result

    def getSecondTag(self, table):
        try:
            self.cursor2.execute("select type,channel from " + table + " group by type")
            result = self.cursor2.fetchall()
        except Exception as info:
            print(info)
            self.connet2 = pymysql.connect(host=self.host2, user=self.user2, password=self.password2,
                                           database=self.database2,
                                           port=self.port, charset=self.charset)
            self.cursor2 = self.connet2.cursor()
            self.cursor2.execute("select type,channel from " + table + " group by type")
            result = self.cursor2.fetchall()
        return result

    def is_exist_tag(self, level, channel):
        try:
            self.cursor.execute(
                "select * from t_carLife_tag where TAG_LEVEL = %s and TAG_NAME = %s ",
                (level, channel))
            if self.cursor.fetchone() is None:
                return False
            return True
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute(
                "select * from t_carLife_tag where TAG_LEVEL = %s and TAG_NAME = %s ",
                (level, channel))
            if self.cursor.fetchone() is None:
                return False
            return True

    def is_exist_media(self, media):
        try:
            self.cursor.execute(
                "select * from t_carLife_media where media_name = %s", media)
            if self.cursor.fetchone() is None:
                return False
            return True
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute(
                "select * from t_carLife_media where media_name = %s", media)
            if self.cursor.fetchone() is None:
                return False
            return True

    def is_exist_url(self, url):
        try:
            self.cursor.execute(
                "select * from t_carLife where spiderurl = %s", url)
            if self.cursor.fetchone() is None:
                return False
            return True
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute(
                "select * from t_carLife where spiderurl = %s", url)
            if self.cursor.fetchone() is None:
                return False
            return True

    def insertTags(self, level, channel, parentId):
        try:
            self.cursor.execute(
                "insert into t_carLife_tag(TAG_LEVEL,TAG_NAME,PARENT_ID,VALID,CDATE) value(%s,%s,%s,%s,%s) ",
                (level, channel, parentId, '1', str(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))))
            self.connet.commit()
            print(u'导入一条标签！标签是：' + channel)
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute(
                "insert into t_carLife_tag(TAG_LEVEL,TAG_NAME,PARENT_ID,VALID,CDATE) value(%s,%s,%s,%s,%s) ",
                (level, channel, parentId, '1', str(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))))
            self.connet.commit()
            print(u'导入一条标签！标签是：' + channel)

    def insertMedia(self, media):
        try:
            self.cursor.execute(
                "insert into t_carLife_media(media_name,VALID,CDATE) value(%s,%s,%s) ",
                (media, '1', str(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))))
            self.connet.commit()
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute(
                "insert into t_carLife_media(media_name,VALID,CDATE) value(%s,%s,%s) ",
                (media, '1', str(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))))
            self.connet.commit()
        print('导入一条媒体！标签是：' + media)

    def saveCarLife(self, media, proCode, cityCode, channelId, typeId, count, valid, times):
        try:
            self.cursor.execute(
                "insert into t_carLife(media_id,province_id,city_id,first_tag,second_tag,carlife_num,VALID,creattime,CDATE) value(%s,%s,%s,%s,%s,%s,%s,%s,%s) ",
                (media, proCode, cityCode, channelId, typeId, count, valid,
                 times, str(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))))
            self.connet.commit()
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute(
                "insert into t_carLife(media_id,province_id,city_id,first_tag,second_tag,carlife_num,VALID,creattime,CDATE) value(%s,%s,%s,%s,%s,%s,%s,%s,%s) ",
                (media, proCode, cityCode, channelId, typeId, count, valid,
                 times, str(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))))
            self.connet.commit()

    def saveCarLifeIC(self, media, count, valid, times):
        try:
            self.cursor.execute(
                "insert into t_carLife(media_id,province_id,city_id,first_tag,second_tag,carlife_num,VALID,creattime,CDATE) value(%s,%s,%s,%s,%s,%s,%s,%s,%s) ",
                (media, '0', '0', '0', '0', count, valid,
                 times, str(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))))
            self.connet.commit()
        except Exception as info:
            print(info)
            self.connet = pymysql.connect(host=self.host, user=self.user, password=self.password,
                                          database=self.database,
                                          port=self.port, charset=self.charset)
            self.cursor = self.connet.cursor()
            self.cursor.execute(
                "insert into t_carLife(media_id,province_id,city_id,first_tag,second_tag,carlife_num,VALID,creattime,CDATE) value(%s,%s,%s,%s,%s,%s,%s,%s,%s) ",
                (media, '0', '0', '0', '0', count, valid,
                 times, str(time.strftime('%Y.%m.%d %H:%M:%S', time.localtime(time.time())))))
            self.connet.commit()
