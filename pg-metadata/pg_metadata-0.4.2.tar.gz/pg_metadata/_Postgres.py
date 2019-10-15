#!/usr/bin/python
# -*- coding: utf-8

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT, ISOLATION_LEVEL_READ_COMMITTED
from psycopg2.extras import RealDictCursor

class Postgres():
    def __init__(self, connect):
        assert connect is not None
        assert isinstance(connect, dict)
        assert len(connect.keys()) > 0

        assert connect.get('host') is not None
        assert connect.get('host').strip() != ''
        self.Host = connect.get("host")

        assert connect.get('port') is not None
        assert connect.get('port') > 0
        self.Port = connect.get("port")

        assert connect.get('database') is not None
        assert connect.get('database').strip() != ''
        self.Database = connect.get("database")

        assert connect.get('username') is not None
        assert connect.get('username').strip() != ''
        self.Username = connect.get("username")

        assert connect.get('password') is not None
        assert connect.get('password').strip() != ''
        self.Password = connect.get("password")

        self.Connection = None
        self.Cursor     = None
        self.Version    = None

    def __str__(self):
        return '%s:%s/%s:%s' % (self.Host, self.Port, self.Database, self.Username)

    def IsConnected(self):
        return self.Connection is not None and self.Cursor is not None

    def GetVersion(self):
        for row in self.Execute("""
            select trim(replace(v.v, 'PostgreSQL ', ''))::integer as version
            from unnest((select regexp_matches(version(), 'PostgreSQL \\d{1,}'))) v
        """):
            self.Version = row.get("version")

    def Connect(self):
        if self.IsConnected():
            self.Disconnect()

        self.Connection = psycopg2.connect(
            host     = self.Host,
            port     = self.Port,
            database = self.Database,
            user     = self.Username,
            password = self.Password
        )
        self.Connection.set_isolation_level(ISOLATION_LEVEL_READ_COMMITTED)
        self.Cursor = self.Connection.cursor(cursor_factory = RealDictCursor)
        self.GetVersion()

    def Disconnect(self):
        if self.Cursor is not None:
            self.Cursor.close()
            self.Cursor = None

        if self.Connection is not None:
            self.Connection.close()
            self.Connection = None

    def Execute(self, query, params=[]):
        if not self.IsConnected():
            self.Connect()

        assert query is not None
        assert query.strip() != ''

        self.Cursor.execute(query, params)
        if self.Cursor.description is not None:
            return self.Cursor.fetchall()

    def CallProc(self, proc_name, params=[]):
        if not self.IsConnected():
            self.Connect()

        assert proc_name is not None
        assert proc_name.strip() != ''

        self.Cursor.callproc(proc_name, params)
        if self.Cursor.description is not None:
            return self.Cursor.fetchall()
