# -*- coding: utf-8 -*-
# @Time    : 2019/10/28 2:54 下午
# @File    : MongodbUtils.py
# @Software: PyCharm

import pymongo

class MongodbUtils(object):
    def __init__(self,host,port,db):
        '''
        获取连接
        :param host:  str
        :param port:  int
        :param db:    str
        '''
        if not isinstance(port,int):
            raise TypeError("port type must be int now is %s"%str(type))
        self.conn = pymongo.MongoClient(host=host, port=port)
        self.db = self.conn[db]

    def is_dict(self,*args):
        '''校验是否是dict'''
        for data in args:
            if not isinstance(data,dict):
                raise TypeError("data type must be dict now is %s"%data)
        return True

    def is_list(self,*args):
        '''校验是否是list'''
        for data in args:
            if not isinstance(data,list):
                raise TypeError("data type must be list now is %s"%data)
        return True


    def update_one(self,collection,term,data):
        '''
        更新一条数据
        :param collection:   集合
        :param term:         更新的条件  {"字段":"值"}
        :param data:         更新的数据  {"字段":"值"}
        :return:    更新条数
        '''
        if self.is_dict(term,data):
            res = self.db[collection].update_one(term,{'$set':data})
            return res.modified_count

    def select_one(self,collection,term):
        '''
        查询一条数据
        :param collection:   集合名称
        :param term:         查询条件  {"字段":"值"}
        :return:   dict
        '''
        if self.is_dict(term):
            res = self.db[collection].find_one(term)
            return res

    def delete_one(self,collection,term):
        '''
        删除一条数据
        :param collection:   集合名称
        :param term:         查询条件  {"字段":"值"}
        :return:   删除条数
        '''
        if self.is_dict(term):
            res = self.db[collection].delete_one(term)
            return res.deleted_count

    def insert_one(self,collection,data):
        '''
        增加一条数据
        :param collection:  集合名称
        :param data:        插入数据 {"字段1":"值1","字段2":"值2"}
        :return:            插入id
        '''
        if self.is_dict(data):
            res = self.db[collection].insert_one(data)
            return res.inserted_id

    def insert_many(self,collection,data):
        '''
        增加一条数据
        :param collection:  集合名称
        :param data:        插入数据 [{"字段1":"值1","字段2":"值2"},{"字段1":"值1","字段2":"值2"}]
        :return:            插入id集合
        '''
        if self.is_list(data):
            res = self.db[collection].insert_many(data)
            return res.inserted_ids

    def close(self):
        '''回收链接'''
        self.conn.close()

if __name__ == '__main__':
    MongodbUtils('11','22','33')