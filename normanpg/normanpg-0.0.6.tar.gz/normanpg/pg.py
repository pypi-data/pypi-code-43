#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created on 9/22/19 by Pat Blair
"""
.. currentmodule:: pg
.. moduleauthor:: Pat Blair <pblair@geo-comm.com>

This module needs a description.
"""
import inspect
import logging
from typing import Any, Iterable, Union
from urllib.parse import urlparse, ParseResult
import psycopg2.extras
import psycopg2.sql
from psycopg2.sql import SQL
import psycopg2.extensions
from .errors import NormanPgException


__logger__ = logging.getLogger(__name__)  #: the module logger

DEFAULT_ADMIN_DB = 'postgres'  #: the default administrative database name
DEFAULT_PG_PORT: int = 5432  #: the default Postgres database port


class InvalidDbResult(NormanPgException):
    """
    Raised in response to an invalid result returned from the database.
    """


def log_query(
        crs: psycopg2.extensions.cursor,
        caller: str,
        query: str or psycopg2.sql.Composed
):
    """
    Log a SQL query.

    :param crs: the execution cursor
    :param caller: the caller
    :param query: the query
    """
    query_str = query if isinstance(query, str) else query.as_string(crs)
    __logger__.debug(f'[{caller}] {query_str}')


def connect(
        url: str,
        dbname: str = None,
        autocommit: bool = False
) -> psycopg2.extensions.connection:
    """
    Get a connection to a Postgres database instance.

    :param url: the instance URL
    :param dbname: the target database name
    :param autocommit: Set the `autocommit` flag on the connection?
    :return: a psycopg2 connection

    .. note::

        If the caller does not provide the `dbname` parameter the function
        creates a connection to the database specified in the URL.
    """
    # Parse the URL.  (We'll need the pieces to construct a connection
    # string.)
    dbp: ParseResult = urlparse(url)
    # Create a dictionary to hold the arguments for the connection.  (We'll
    # unpack it later.)
    cnx_opt = {
        k: v for k, v in
        {
            'host': dbp.hostname,
            'port': int(dbp.port) if dbp.port is not None else DEFAULT_PG_PORT,
            'database': dbname if dbname is not None else dbp.path[1:],
            'user': dbp.username,
            'password': dbp.password
        }.items() if v is not None
    }
    cnx = psycopg2.connect(**cnx_opt)
    # If the caller requested that the 'autocommit' flag be set...
    if autocommit:
        # ...do that now.
        cnx.autocommit = True
    return cnx


def _execute_scalar(
        cnx: psycopg2.extensions.connection,
        query: psycopg2.sql.Composed,
        caller: str
) -> Any:
    """
    This is a helper function for :py:func:`execute_scalar` that executes a
    query on an open cursor.

    :param cnx: an open connection or database connection string
    :param query: the query
    :param caller: identifies the call stack location
    """
    with cnx.cursor() as crs:
        # Log the query.
        log_query(crs=crs, caller=caller, query=query)
        # Execute!
        try:
            crs.execute(query)
        except SyntaxError:
            logging.exception(query.as_string(crs))
            raise
        # Get the first column from the first result.
        return crs.fetchone()[0]


def execute_scalar(
        cnx: Union[str, psycopg2.extensions.connection],
        query: Union[str, psycopg2.sql.Composed],
        caller: str = None
) -> Any or None:
    """
    Execute a query that returns a single, scalar result.

    :param cnx: an open psycopg2 connection or the database URL
    :param query: the `psycopg2` composed query
    :param caller: identifies the caller (for diagnostics)
    :return: the scalar string result (or `None` if the query returns no
        result)
    """
    # Get the name of the calling function so we can include it in the logging
    # statement.
    caller = caller if caller else inspect.stack()[1][3]
    # Make sure the query is `Composed`.
    _query = (
        psycopg2.sql.SQL(query).string
        if isinstance(query, str)
        else query
    )
    # If the caller passed us a connection string...
    if isinstance(cnx, str):
        # ...get a connection and use the helper method to execute the query.
        with connect(url=cnx) as _cnx:
            return _execute_scalar(cnx=_cnx, query=_query, caller=caller)
    # It looks as though we were given an open connection, so execute the
    # query on it.
    return _execute_scalar(cnx=cnx, query=_query, caller=caller)


def _execute_rows(
        cnx: psycopg2.extensions.connection,
        query: psycopg2.sql.Composed,
        caller: str
) -> Iterable[psycopg2.extras.DictRow]:
    """
    This is a helper function for :py:func:`execute_rows` that executes a
    query on an open cursor.

    :param cnx: an open connection or database connection string
    :param query: the query
    :param caller: identifies the call stack location
    :return: an iteration of `DictRow` instances representing the rows
    """
    with cnx.cursor(cursor_factory=psycopg2.extras.DictCursor) as crs:
        # Log the query.
        log_query(crs=crs, caller=caller, query=query)
        # Execute!
        try:
            crs.execute(query)
        except SyntaxError:
            logging.exception(query.as_string(crs))
            raise
        # Fetch the rows and yield them to the caller.
        for row in crs:
            yield row


def execute_rows(
        cnx: Union[str, psycopg2.extensions.connection],
        query: Union[str, psycopg2.sql.Composed],
        caller: str = None
) -> Iterable[psycopg2.extras.DictRow]:
    """
    Execute a query that returns an iteration of rows.

    :param cnx: an open connection or database connection string
    :param query: the `psycopg2` composed query
    :param caller: identifies the caller (for diagnostics)
    :return: an iteration of `DictRow` instances representing the row
    """
    # Get the name of the calling function so we can include it in the logging
    # statement.
    caller = caller if caller else inspect.stack()[1][3]
    # Make sure the query is `Composed`.
    _query = (
        psycopg2.sql.SQL(query).string
        if isinstance(query, str)
        else query
    )
    # If the caller passed us a connection string...
    if isinstance(cnx, str):
        # ...get a connection and use the helper method to execute the query.
        with connect(url=cnx) as _cnx:
            for row in _execute_rows(cnx=_cnx, query=_query, caller=caller):
                yield row
    # It looks as though we were given an open connection, so execute the
    # query on it.
    for row in _execute_rows(cnx=cnx, query=_query, caller=caller):
        yield row


def _execute(
        cnx: psycopg2.extensions.connection,
        query: psycopg2.sql.Composed,
        caller: str
):
    """
    This is a helper function for :py:func:`execute` that executes a
    query on an open cursor.

    :param cnx: an open connection or database connection string
    :param query: the query
    :param caller: identifies the call stack location
    """
    with cnx.cursor() as crs:
        # Log the query.
        log_query(crs=crs, caller=caller, query=query)
        # Execute!
        try:
            crs.execute(query)
        except SyntaxError:
            logging.exception(query.as_string(crs))
            raise


def execute(
        cnx: Union[str, psycopg2.extensions.connection],
        query: Union[str, psycopg2.sql.Composed],
        caller: str = None
):
    """
    Execute a query that returns no result.

    :param cnx: an open connection or database connection string
    :param query: the `psycopg2` composed query
    :param caller: identifies the caller (for diagnostics)

    .. seealso::

        * :py:func:`execute_scalar`
        * :py:func:`execute_rows`
    """
    # Get the name of the calling function so we can include it in the logging
    # statement.
    caller = caller if caller else inspect.stack()[1][3]
    # Make sure the query is `Composed`.
    _query = (
        psycopg2.sql.SQL(query).string
        if isinstance(query, str)
        else query
    )
    # If the caller passed us a connection string...
    if isinstance(cnx, str):
        # ...get a connection and use the helper method to execute the query.
        with connect(url=cnx) as _cnx:
            _execute(cnx=_cnx, query=_query, caller=caller)
    # It looks as though we were given an open connection, so execute the
    # query on it.
    _execute(cnx=cnx, query=_query, caller=caller)


def compose_table(
        table_name: str,
        schema_name: str = None
) -> psycopg2.sql.Composed:
    """
    Get a composed SQL object for a fully-qualified table name.

    :param table_name: the table name
    :param schema_name: the schema name
    :return: a composed SQL object
    """
    if schema_name is not None:
        return psycopg2.sql.SQL('{}.{}').format(
            SQL(schema_name),
            SQL(table_name)
        )
    return SQL('{}').format(SQL(table_name))
