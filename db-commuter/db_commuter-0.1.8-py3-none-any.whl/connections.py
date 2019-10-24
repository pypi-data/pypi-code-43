# -*- coding: utf-8 -*-

"""Connection to database
"""
import abc
from contextlib import contextmanager

import psycopg2
from sqlalchemy import create_engine
import sqlite3

__all__ = [
    "SQLiteConnector",
    "PgConnector"
]


class BaseConnector(abc.ABC):
    """Setting basic connection parameters
    """
    def __init__(self, **kwargs):
        """
        Args:
            conn: connection to database
            engine: SQLAlchemy engine
        """
        self.conn = None
        self.engine = None

    def __del__(self):
        """Close connection and dispose engine when class object is garbage collected.
        """
        self.close_connection()

    @abc.abstractmethod
    def make_engine(self):
        raise NotImplementedError()

    @contextmanager
    def make_connection(self):
        if self.conn is None:
            self.set_connection()

        yield self.conn

        self.close_connection()

    @abc.abstractmethod
    def set_connection(self, **kwargs):
        raise NotImplementedError()

    def close_connection(self):
        if self.conn is not None:
            self.conn.close()
            self.conn = None


class SQLiteConnector(BaseConnector):
    """Establish connection with SQLite database.
    """
    def __init__(self, path2db):
        """
        Args:
            path2db (str): path to database file
        """
        super().__init__()

        self.path2db = path2db
        self.engine = self.make_engine()

    def make_engine(self):
        return create_engine('sqlite:///' + self.path2db, echo=False)

    def set_connection(self):
        self.conn = sqlite3.connect(self.path2db)


class PgConnector(BaseConnector):
    """Establish connection with PostgreSQL database.
    """
    def __init__(self, host, port, user, password, db_name, **kwargs):
        """Besides the basic connection parameters any other connection parameter
        supported by psycopg2.connect can be passed by keyword.

        Args:
            host (str):
            port (str):
            user (str):
            password (str):
            db_name (str):

        Keyword Args:
            schema (str): specifying schema prevents from explicit specification in class methods
        """
        super().__init__()
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db_name = db_name
        self.schema = kwargs.get('schema', None)

        self.conn_params = {}

        for key in kwargs.keys():
            if key not in ['schema']:
                self.conn_params[key] = kwargs.get(key)

        self.engine = self.make_engine()

    def make_engine(self):
        engine = 'postgresql://' + self.user + ':' + self.password + '@' + \
            self.host + ':' + self.port + '/' + self.db_name

        for key in self.conn_params.keys():
            engine += '?' + key + '=' + self.conn_params[key]

        if self.schema is None:
            return create_engine(engine)
        else:
            return create_engine(
                engine,
                connect_args={'options': '-csearch_path={}'.format(self.schema)})

    def set_connection(self, **kwargs):
        """Initialize connection using psycopg2.connect.
        """
        if self.schema is None:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.db_name,
                **self.conn_params)
        else:
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                dbname=self.db_name,
                options=f'--search_path={self.schema}',
                **self.conn_params)

