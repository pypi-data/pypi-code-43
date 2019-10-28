# -*- coding: utf-8 -*-
# @Time    : 2019/10/28 2:54 下午
# @File    : MongodbUtils.py
# @Software: PyCharm

import pymongo

class MongodbUtils(object):
    def __init__(self,host,port,db):
        self.conn = pymongo.MongoClient(host=host,port=port)
        self.db = self.conn[db]

    def update_one(self,collection,term,data):
        '''
        更新一条数据
        :param collection:   集合
        :param term:         更新的条件  {"字段":"值"}
        :param data:         更新的数据  {"字段":"值"}
        :return:    更新条数
        '''
        res = self.db[collection].update_one(term,{'$set':data})
        return res.modified_count

    def select_one(self,collection,term):
        '''
        查询一条数据
        :param collection:   集合名称
        :param term:         查询条件  {"字段":"值"}
        :return:   dict
        '''
        res = self.db[collection].find_one(term)
        return res

    def delete_one(self,collection,term):
        '''
        删除一条数据
        :param collection:   集合名称
        :param term:         查询条件  {"字段":"值"}
        :return:   删除条数
        '''
        res = self.db[collection].delete_one(term)
        return res.deleted_count

    def insert_one(self,collection,data):
        '''
        增加一条数据
        :param collection:  集合名称
        :param data:        插入数据 {"字段1":"值1","字段2":"值2"}
        :return:            插入id
        '''
        res = self.db[collection].insert_one(data)
        return res.inserted_id

    def insert_many(self,collection,data):
        '''
        增加一条数据
        :param collection:  集合名称
        :param data:        插入数据 [{"字段1":"值1","字段2":"值2"},{"字段1":"值1","字段2":"值2"}]
        :return:            插入id集合
        '''
        res = self.db[collection].insert_many(data)
        return res.inserted_ids

    def close(self):
        '''回收链接'''
        self.conn.close()

if __name__ == '__main__':
    pass