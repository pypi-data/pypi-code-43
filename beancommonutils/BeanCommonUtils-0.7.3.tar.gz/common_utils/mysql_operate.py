# -*- coding: utf-8 -*-

import pymysql


class MysqlOperate:

    @classmethod
    def mysql_conn(cls, mysql_info):
        host = mysql_info['host']
        user_name = mysql_info['user_name']
        passwd = mysql_info['passwd']
        dbname = mysql_info['dbname']
        if mysql_info.__contains__('port'):
            port = mysql_info['port']
        else:
            port = 3306
        db = pymysql.connect(host, user_name, passwd, dbname, port, charset="utf8")
        cursor = db.cursor()
        return db, cursor

    @classmethod
    def mysql_query(cls, mysql_info, query):
        db, cursor = cls.mysql_conn(mysql_info)

        cursor.execute(query)
        # 获取所有字段名称
        col_name_list = [tuple_data[0] for tuple_data in cursor.description]
        results = cursor.fetchall()
        result_list = []
        for row in results:
            result_list.append(row)

        db.close()
        return result_list, col_name_list

    @classmethod
    def mysql_insert(cls, mysql_info, query):
        db, cursor = cls.mysql_conn(mysql_info)
        cursor.execute(query)
        db.commit()
        db.close()

    @classmethod
    def mysql_insert_mul(cls, mysql_info, queries):
        db, cursor = cls.mysql_conn(mysql_info)
        for query in queries:
            cursor.execute(query)
            db.commit()

        db.close()
