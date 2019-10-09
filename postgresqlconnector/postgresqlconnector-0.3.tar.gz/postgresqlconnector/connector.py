import psycopg2
from psycopg2.extras import NamedTupleCursor
from psycopg2.extensions import connection
from collections import namedtuple
from typing import List, Type


__all__ = ['DB']


class DB:
    _connection: connection = None

    def __init__(self):
        raise Exception('DB is singleton')

    @classmethod
    def query(cls, sql: str, params: dict = None) -> List[namedtuple] or None:
        cursor = cls._query(sql, params)
        if cursor.rowcount == -1:
            return None
        try:
            result = cursor.fetchall()
        except psycopg2.ProgrammingError:
            return None
        return result

    @classmethod
    def row(cls, sql: str, params: dict = None) -> namedtuple:
        cursor = cls._query(sql, params)
        row = cursor.fetchone()
        return row

    @classmethod
    def scalar(cls, sql: str, params: dict = None) -> Type:
        row = cls.row(sql, params)
        return row[0]

    @classmethod
    def _get_connection(cls,
                        host='localhost',
                        port='5432',
                        dbname='postgres',
                        user='postgres',
                        password='postgres') -> connection:
        if not DB._connection:
            DB._connection = psycopg2.connect(
                host=host,
                port=port,
                dbname=dbname,
                user=user,
                password=password
            )

        return DB._connection

    @classmethod
    def _query(cls, sql: str, params: dict = None) -> NamedTupleCursor:
        conn = cls._get_connection()
        cursor = conn.cursor(cursor_factory=NamedTupleCursor)
        cursor.execute(sql, params)
        conn.commit()
        return cursor

    def __del__(self):
        if DB._connection:
            DB._connection.close()
