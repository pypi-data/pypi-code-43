import psycopg2
from psycopg2.extras import NamedTupleCursor
from psycopg2.extensions import connection
from collections import namedtuple
from typing import List, Type
import atexit
from .transaction import Transaction, CreateTransactionException


__all__ = ['DB']


class DB:
    _connection: connection = None
    _connection_info = {
        'host': 'localhost',
        'port': '5432',
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'postgres',
    }
    _transaction: Transaction = None

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
    def set_connection_info(cls,
                            host: str = None,
                            port: int = None,
                            dbname: str = None,
                            user: str = None,
                            password: str = None):
        if cls._connection:
            cls._connection.close()

        for value, param in zip(
            [host, port, dbname, user, password],
            ['host', 'port', 'dbname', 'user', 'password']
        ):
            if value:
                cls._connection_info[param] = value

    @classmethod
    def create_transaction(cls) -> Transaction:
        if cls._transaction:
            raise CreateTransactionException()

        cls._transaction = Transaction(cls)
        return cls._transaction

    @classmethod
    def close_transaction(cls, rollback=False):
        cls._transaction = None
        if rollback:
            cls._connection.rollback()
        else:
            cls._connection.commit()

    @classmethod
    def _get_connection(cls) -> connection:
        if not DB._connection:
            DB._connection = psycopg2.connect(**cls._connection_info)

        return DB._connection

    @classmethod
    def _query(cls, sql: str, params: dict = None) -> NamedTupleCursor:
        conn = cls._get_connection()
        cursor = conn.cursor(cursor_factory=NamedTupleCursor)
        cursor.execute(sql, params)

        if not cls._transaction:
            conn.commit()

        return cursor

    @classmethod
    def exit(cls):
        if cls._connection:
            cls._connection.close()
            cls._connection = None


@atexit.register
def _destructor():
    DB.exit()
