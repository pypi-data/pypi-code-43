# -*- coding: utf-8 -*-

"""Collection of methods for communication with database.
"""
import abc
from io import StringIO

import pandas as pd
import psycopg2
from sqlalchemy import exc

from db_commuter.connections import *

__all__ = [
    "SQLiteCommuter",
    "PgCommuter"
]


class Commuter(abc.ABC):
    def __init__(self, connector):
        self.connector = connector

    @abc.abstractmethod
    def select(self, cmd, **kwargs):
        """Select data from table and return it in Pandas.DataFrame.
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def insert(self, obj, data, **kwargs):
        """Insert from Pandas.DataFrame to table.
        """
        raise NotImplementedError()


class SQLCommuter(Commuter):
    """Parent class for SQL-like databases.
    """
    def __init__(self, connector):
        super().__init__(connector)

    @abc.abstractmethod
    def delete_table(self, table_name, **kwargs):
        raise NotImplementedError()

    @abc.abstractmethod
    def is_table_exist(self, table_name):
        raise NotImplementedError()

    @abc.abstractmethod
    def execute(self, cmd, vars=None, commit=True):
        """Execute SQL command.

        Args:
            cmd (str): SQL query
            vars: parameters to command, may be provided as sequence or mapping
            commit (boolean): persist changes to database if True
        """
        raise NotImplementedError()

    @abc.abstractmethod
    def execute_script(self, path2script, commit=True):
        """Execute multiple SQL statements separated by semicolon.
        """
        raise NotImplementedError()

    def select(self, cmd, **kwargs):
        with self.connector.engine.connect() as conn:
            data = pd.read_sql_query(cmd, conn)

        return data

    def insert(self, table_name, df, **kwargs):
        """Insert from Pandas.DataFrame.

        Args:
            table_name (str): name of the table where to insert.
            df (Pandas.DataFrame): from where to insert.

        Keyword Args:
            schema: specify the schema, if None, use the default schema.
            chunksize: rows will be written in batches of this size at a time.

        Raises:
             ValueError: if insert fails.
        """
        schema = kwargs.get('schema', None)
        chunksize = kwargs.get('chunksize', None)

        with self.connector.engine.connect() as conn:
            try:
                df.to_sql(table_name,
                          con=conn,
                          schema=schema,
                          if_exists='append',
                          index=False,
                          chunksize=chunksize)
            except (ValueError, exc.IntegrityError) as e:
                raise ValueError(e)


class SQLiteCommuter(SQLCommuter):
    """Methods for communication with SQLite database.
    """
    def __init__(self, path2db):
        super().__init__(SQLiteConnector(path2db))

    def delete_table(self, table_name, **kwargs):
        self.execute('drop table if exists %s' % table_name)

    def is_table_exist(self, table_name):
        cmd = 'select name from sqlite_master where type=\'table\' and name=\'%s\'' % table_name

        data = self.select(cmd)

        if len(data) > 0:
            return data.name[0] == table_name

        return False

    def execute(self, cmd, vars=None, commit=True):
        # set the connection
        with self.connector.make_connection() as conn:
            # create cursor object
            cur = conn.cursor()
            # execute sql command
            if vars is None:
                cur.execute(cmd)
            else:
                cur.execute(cmd, vars)

            # save the changes
            if commit:
                conn.commit()

        # close the connection
        self.connector.close_connection()

    def execute_script(self, path2script, commit=True):
        with open(path2script, 'r') as fh:
            script = fh.read()

        with self.connector.make_connection() as conn:
            cur = conn.cursor()
            cur.executescript(script)

            if commit:
                conn.commit()

        self.connector.close_connection()


class PgCommuter(SQLCommuter):
    """Methods for communication with PostgreSQL database.
    """
    def __init__(self, host, port, user, password, db_name, **kwargs):
        super().__init__(PgConnector(host, port, user, password, db_name, **kwargs))

    @classmethod
    def from_dict(cls, params, **kwargs):
        """Alternative constructor used access parameters from dictionary.
        """
        return cls(params['host'], params['port'], params['user'],
                   params['password'], params['db_name'], **kwargs)

    def execute(self, cmd, vars=None, commit=True):
        # set the connection
        with self.connector.make_connection() as conn:
            # create cursor object
            try:
                with conn.cursor() as cur:
                    # execute sql command
                    if vars is None:
                        cur.execute(cmd)
                    else:
                        cur.execute(cmd, vars)

                # commit the changes
                if commit:
                    conn.commit()
            except psycopg2.DatabaseError as e:
                # roll back the pending transaction
                if commit:
                    conn.rollback()
                raise e

        self.connector.close_connection()

    def execute_script(self, path2script, commit=True):
        with open(path2script, 'r') as fh:
            script = fh.read()

        with self.connector.make_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(script)

            if commit:
                conn.commit()

        self.connector.close_connection()

    def insert_fast(self, table_name, df):
        """Place Pandas.DataFrame to buffer and use copy_from method for insert.

        Args:
            table_name (str): name of the table where to insert.
            df (Pandas.DataFrame): from where to insert.
        """
        with self.connector.make_connection() as conn:
            with conn.cursor() as cur:
                # put pandas frame to buffer
                s_buf = StringIO()
                df.to_csv(s_buf, index=False, header=False)
                s_buf.seek(0)
                # insert to table
                try:
                    cur.copy_from(s_buf, table_name, sep=',', null='')
                except (ValueError, exc.ProgrammingError, psycopg2.ProgrammingError, psycopg2.IntegrityError) as e:
                    raise ValueError(e)

            conn.commit()

        self.connector.close_connection()

    def delete_table(self, table_name, **kwargs):
        """Delete table.

        Args:
            table_name (str): name of the table to delete

        Keyword Args:
            schema (str): name of the database schema
            cascade (boolean): True if delete cascade
        """
        schema = kwargs.get('schema', None)
        cascade = kwargs.get('cascade', False)

        table_name = self.__get_table_name(schema, table_name)

        if cascade:
            self.execute('drop table if exists %s cascade' % table_name)
        else:
            self.execute('drop table if exists %s' % table_name)

    def is_table_exist(self, table_name):
        schema = self.connector.schema

        if schema is None:
            schema = 'public'

        with self.connector.make_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "select * from information_schema.tables where table_name=%s and table_schema=%s",
                    (table_name, schema))

        self.connector.close_connection()

        return bool(cur.rowcount)

    def get_connections_count(self):
        """Returns the amount of active connections.
        """
        cmd = \
            f'select sum(numbackends) ' \
            f'from pg_stat_database'

        df = self.select(cmd)

        return df.iloc[0][0]

    def resolve_primary_conflicts(self, table_name, df, p_key, filter_col):
        """Resolve primary key conflicts in DataFrame.

        Method selects data from ``table_name`` where value in ``filter_col``
        is greater or equal the minimal found value in ``filter_col`` of the given DataFrame.
        Rows having primary key already presented in selected data are deleted from DataFrame.

        Args:
            table_name (str): Name of the table.
            df (pd.DataFrame): DataFrame from where rows having existing primary key need to be deleted.
            p_key (List): primary key columns.
            filter_col (str): column used when querying the data from table.

        Returns:
            pd.DataFrame
        """
        _df = df.copy()

        min_val = _df[filter_col].min()

        if isinstance(min_val, pd.Timestamp):
            cmd = f"select * from {table_name} where {filter_col} >= \'{min_val}\'"
        else:
            cmd = f"select * from {table_name} where {filter_col} >= {min_val}"

        # select from table
        table_data = self.select(cmd)

        # remove conflicting rows
        if not table_data.empty:
            _df.set_index(p_key, inplace=True)
            table_data.set_index(p_key, inplace=True)

            # remove rows which are in table data index
            _df = _df[~_df.index.isin(table_data.index)]

            _df = _df.reset_index(level=p_key)

        return _df

    def resolve_foreign_conflicts(self, parent_table_name, df, f_key, filter_parent, filter_child):
        """Resolve foreign key conflicts in DataFrame.

        Method selects data from ``parent_table_name`` where value in ``filter_parent`` column
        is greater or equal the minimal found value in ``filter_child`` column of the given DataFrame.
        Rows having foreign key already presented in selected data are deleted from DataFrame.

        Args:
            parent_table_name (str): Name of the parent table.
            df (pd.DataFrame): DataFrame from where rows having existing foreign key need to be deleted.
            f_key (List): foreign key columns.
            filter_parent (str): column used when querying the data from parent table.
            filter_child (str): column used when searching for minimal value in child.

        Returns:
            pd.DataFrame
        """
        _df = df.copy()

        min_val = df[filter_child].min()

        if isinstance(min_val, pd.Timestamp):
            cmd = f"select * from {parent_table_name} where {filter_parent} >= \'{min_val}\'"
        else:
            cmd = f"select * from {parent_table_name} where {filter_parent} >= {min_val}"

        table_data = self.select(cmd)

        # remove conflicting rows
        if not table_data.empty:
            _df.set_index(f_key, inplace=True)
            table_data.set_index(f_key, inplace=True)

            # remove rows which are not in parent index
            _df = _df[_df.index.isin(table_data.index)]

            _df = _df.reset_index(level=f_key)
        else:
            # if parent is empty then cannot insert data
            _df = pd.DataFrame()

        return _df

    @staticmethod
    def __get_table_name(schema, table_name):
        if schema is None:
            return table_name
        return schema + '.' + table_name

