# -*- coding: utf-8 -*-
"""MySQL class file."""

import pymysql
import re
import sys


class MySQL(object):
    """MySQL base class definition."""

    def __init__(
        self,
        server,
        port,
        user,
        password,
        db,
        verbose=False,
    ):
        """Initialize an instance."""
        # create a connection to the MySQL database
        if re.match('^/', server):
            # connect to mysql as a socket
            try:
                self.db = pymysql.connect(
                    unix_socket=server,
                    user=user,
                    passwd=password,
                    db=db,
                )
            except Exception as e:
                print('ERROR: MySQL socket connection failed: %s' % (server))
                print(e)
                sys.exit(1)
        else:
            # connect to mysql as a tcp host:port connection
            try:
                self.db = pymysql.connect(
                    host=server,
                    port=port,
                    user=user,
                    passwd=password,
                    db=db,
                )
            except Exception as e:
                print('ERROR: MySQL TCP connection failed: %s' % (server))
                print(e)
                sys.exit(1)
        self.pymysql = pymysql

    def create_dictcursor(self):
        """Return a new cursor based off of DictCursor."""
        return self.db.cursor(pymysql.cursors.DictCursor)

    def get_one_row(self, table, field, value):
        """Return a single row matching field=value."""
        cur = self.create_dictcursor()
        query_string = 'SELECT * FROM %s WHERE %s = %s LIMIT 1'
        cur.execute(query_string % (table, field, value))
        for row in cur:
            return row

    def get_table(self, table_name):
        """Return all rows in the given table in dictionary form."""
        cur = self.create_dictcursor()
        cur.execute('SELECT * FROM %s;' % (table_name))
        return list(cur)

    def get_table_dict(self, table_name, key='id'):
        """Return a dictionary of table rows indexed by key."""
        rows = self.get_table(table_name)
        table = {}
        for row in rows:
            index = row.get(key)
            table[index] = row
        return table
