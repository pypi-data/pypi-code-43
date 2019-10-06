# -*- coding: utf-8 -*-
# @Time    : 2019/10/6 9:08 上午
# @File    : Sqlite3Utils.py
# @Software: PyCharm

import sqlite3

class Sqlite3Utils(object):
    '''
    操作sqlite3工具类
    '''
    def __init__(self,db_path):
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()

    def select_sqlite3(self,sql,param=None):
        '''
        查询方法
        :param sql:  select * from test where id=?
        :param param: ('1',)
        :return:
        '''
        if param:
            res = self.cursor.execute(sql,param)
        else:
            res = self.cursor.execute(sql)
        return self.cursor.fetchall()

    def intsert_sqlite3(self,sql,param=None):
        '''
        插入方法
        :param sql:
        :param param:
        :return:  插入条数
        '''
        if param:
            self.cursor.execute(sql,param)
        else:
            self.cursor.execute(sql)
        self.conn.commit()
        return self.cursor.rowcount

    def update_sqlite3(self,sql,param=None):
        if param:
            self.cursor.execute(sql,param)
        else:
            self.cursor.execute(sql)
        self.conn.commit()
        return self.cursor.rowcount

    def delete_sqlite3(self,sql,param):
        if param:
            self.cursor.execute(sql,param)
        else:
            self.cursor.execute(sql)
        self.conn.commit()
        return self.cursor.rowcount

    def close(self):
        self.cursor.close()
        self.conn.close()

if __name__ == '__main__':
    conn = Sqlite3Utils('test.db')
    sql = 'INSERT INTO "main"."test"("id", "test") VALUES (?,?);'
    sql1 = 'select * from "main"."test" where id=?'
    sql2 = 'delete from "main"."test" where id=?'
    sql3 = 'update "main"."test" set test=? where id=?'
    print(conn.intsert_sqlite3(sql,('11','222',)))
    print(conn.select_sqlite3(sql1,('11',)))
    print(conn.update_sqlite3(sql3,('333','11')))
    print(conn.delete_sqlite3(sql2,('11',)))
