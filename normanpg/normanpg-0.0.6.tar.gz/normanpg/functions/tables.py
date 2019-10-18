#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 9/29/19
"""
.. currentmodule:: normanpg.functions.srs
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module contains table-level functions.
"""
from typing import Union
from phrasebook import SqlPhrasebook
import psycopg2.extensions
from psycopg2.sql import SQL, Literal
from ..errors import NormanPgException
from ..pg import connect, execute_rows, execute_scalar

_PHRASEBOOK = SqlPhrasebook().load()


class InvalidSrsException(NormanPgException):
    """
    Raised if an attempt is made to reference an invalid spatial reference
    system (SRS).
    """


class TooManyGeometryColumns(NormanPgException):
    """
    Raised if an attempt is made to access a table with multiple geometry
    columns.
    """


class NoGeometryColumn(NormanPgException):
    """
    Raised if an attempt is made to access non-existent geometries.
    """


def table_exists(
        cnx: Union[str, psycopg2.extensions.connection],
        table_name: str,
        schema_name: str
) -> bool:
    """

    :param cnx: an open connection or database connection string
    :param table_name: the name of the table
    :param schema_name: the name of the schema in which the table resides
    :return: ``True`` if the table exists, otherwise ``False``
    """
    query = SQL(_PHRASEBOOK.gets('table_exists')).format(
        table=Literal(table_name),
        schema=Literal(schema_name)
    )
    return execute_scalar(cnx=cnx, query=query)


def geometry_column(
        cnx: Union[str, psycopg2.extensions.connection],
        table_name: str,
        schema_name: str
) -> str or None:
    """
    Get the name of the geometry column in a feature table.

    :param cnx: an open connection or database connection string
    :param table_name: the name of the table
    :param schema_name:
    :return: the name of the geometry column
    """
    query = SQL(_PHRASEBOOK.gets('geometry_column')).format(
        table=Literal(table_name),
        schema=Literal(schema_name)
    )
    results = list(execute_rows(cnx=cnx, query=query))
    if not results:
        return None
    elif len(results) > 1:
        raise TooManyGeometryColumns('The table has multiple geometry columns.')
    return results[0][0]


def srid(
        cnx: Union[str, psycopg2.extensions.connection],
        table_name: str,
        schema_name: str
) -> int:
    """
    Get the SRID for geometries in a feature table.

    :param cnx: an open connection or database connection string
    :param table_name: the name of the table
    :param schema_name: the name of the schema in which the table resides
    :return: the SRID for geometries in the table
    """
    # We need to make multiple database calls, so if we were passed a string...
    if isinstance(cnx, str):
        # ...create a connection...
        _cnx = connect(cnx)
        # ...and note that we need to close it.
        close = True
    else:
        # Otherwise, the connection is just an open connection and this call
        # is just part of the stream.
        _cnx = cnx
        close = False

    try:
        _geometry_column = geometry_column(
            cnx=_cnx,
            table_name=table_name,
            schema_name=schema_name
        )
        if not _geometry_column:
            raise NoGeometryColumn(
                'No geometry column is associated with the specified table '
                'and schema names.'
            )
        query = SQL(_PHRASEBOOK.gets('srid')).format(
            table=Literal(table_name),
            schema=Literal(schema_name),
            geomcol=Literal(_geometry_column)
        )
        return execute_scalar(cnx=cnx, query=query)
    finally:
        if close:
            _cnx.close()
