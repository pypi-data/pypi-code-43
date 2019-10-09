import mysql.connector

__all__ = ["MySQLUtils"]

class MonoDB(object):
    def __init__(self, host, user, passwd, database):
        self._conn = mysql.connector.connect(host, user, passwd, database)
        self._curs = self._conn.cursor(dictionary=True)

    @property
    def conn(self):
        return self._conn

    @property
    def curs(self):
        return self._curs
    

class MySQLUtils(object):
    def __init__(self, host="localhost", user="root", passwd="123456", database="demo"):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.database = database
    
    def _get_db(self):
        return MonoDB(self.host, self.user, self.passwd, self.database)

    def execute_mysql_cmd(self, sql, val, mode="read"):
        monodb = self._get_db()
        if mode == "read":
            monodb.curs.execute(sql, val)
            return monodb.curs.fetchall()
        else:
            monodb.curs.execute(sql, val)

    def delete_table_row(self, table_name, key_name, key):
        monodb = self._get_db()
        sql = 'delete from ' + table_name + ' where ' + key_name + '=%s'
        val = (key, )
        monodb.curs.execute(sql, val)

    def get_table_column_value(self, table_name, key_name, column_name, key, similar=False, order=""):
        monodb = self._get_db()
        condition = ""
        val = ()
        if key:
            condition = '=%s' if not similar else ' like "%"%s"%"'
            condition = ' WHERE ' + key_name + condition
            val = (key, )
        sql = 'SELECT ' + column_name + ' FROM ' + table_name +  condition + ' ' + order
        monodb.curs.execute(sql, val)
        return monodb.curs.fetchall()

    def get_multi_columns_given_multi_keys(self, table_name, keys, columns="*"):
        monodb = self._get_db()
        target = columns if columns == "*" else ", ".join(columns)
        sql = "SELECT " + target + " FROM " + table_name + " WHERE "  + " and ".join([i[0] + "=%s" for i in keys])
        val = tuple([i[1] for i in keys])
        monodb.curs.execute(sql, val)
        rows = monodb.curs.fetchall()
        return None if not rows else rows[0]

    def get_table_row(self, table_name, key_name, key):
        monodb = self._get_db()
        sql = "SELECT * FROM " + table_name + " WHERE " + key_name + "=%s"
        val = (key, )
        monodb.curs.execute(sql, val)
        rows = monodb.curs.fetchall()
        return None if not rows else rows[0]

    def set_table_column_value(self, table_name, key_name, column_name, key, column):
        monodb = self._get_db()
        sql = "UPDATE " + table_name + " SET " + column_name + "=%s WHERE "  + key_name + "=%s"
        val = (column, key)
        monodb.curs.execute(sql, val)
        monodb.conn.commit()

    def set_table_multi_column_values(self, table_name, key_name, key, columns):
        for (column_name, column) in columns:
            set_table_column_value(table_name, key_name, column_name, key, column)

    def set_table_column_value_given_multi_keys(self, table_name, keys, column_name, column):
        monodb = self._get_db()
        sql = "UPDATE " + table_name + " SET " + column_name + "=%s WHERE "  + " and ".join([i[0] + "=%s" for i in keys])
        val = (column, ) + tuple([i[1] for i in keys])
        monodb.curs.execute(sql, val)
        monodb.conn.commit()
    
    def set_table_multi_column_values_given_multi_keys(self, table_name, keys, columns):
        for (column_name, column) in columns:
            set_table_column_value_given_multi_keys(table_name, keys, column_name, column)

    def insert_table_row_from_dict(self, table_name, dic):
        monodb = self._get_db()
        sql = "INSERT INTO " + table_name + " (" + ", ".join(dic.keys()) + ") VALUES (%s" + " ,%s" * (len(dic.keys()) - 1) + ")"
        val = tuple(dic.values())
        monodb.curs.execute(sql, val)
        monodb.conn.commit()

    def insert_or_update_table_row(self, table_name, dic, key_name):
        if not get_table_row(table_name, key_name, dic[key_name]):
            insert_table_row_from_dict(table_name, dic)
        else:
            set_table_multi_column_values(table_name, key_name, dic[key_name], dic.items())

    def insert_or_update_row_given_multi_keys(self, table_name, dic, keys):
        keys = [(i, dic[i]) for i in keys]
        if not get_multi_columns_given_multi_keys(table_name, keys):
            insert_table_row_from_dict(table_name, dic)
        else:
            set_table_multi_column_values_given_multi_keys(table_name, keys, dic.items())
