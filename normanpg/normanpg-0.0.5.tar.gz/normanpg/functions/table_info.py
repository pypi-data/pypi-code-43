#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 9/29/19
"""
.. currentmodule:: normanpg.functions.srs
.. moduleauthor:: Pat Daburu <pat@daburu.net>

If you're dealing with
`spatial reference systems <https://en.wikipedia.org/wiki/Spatial_reference_system>`_
we have some functions for you.
"""
from typing import Union
from phrasebook import SqlPhrasebook
import psycopg2.extensions
from psycopg2.sql import SQL, Literal
from ..errors import NormanPgException
from ..pg import connect, execute_rows, execute_scalar

_phrasebook = SqlPhrasebook().load()


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
    query = SQL(_phrasebook.gets('table_exists')).format(
        table=Literal(table_name),
        schema=Literal(schema_name)
    )
    return execute_scalar(cnx=cnx,query=query)


def geometry_column(
        cnx: Union[str, psycopg2.extensions.connection],
        table_name: str,
        schema_name: str
) -> str or None:
    query = SQL(_phrasebook.gets('geometry_column')).format(
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
    # If we were passed a string...
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
            # TODO: Consider checking if the table exists and raising a more specific error.
            raise NoGeometryColumn(
                'No geometry column is associated with the specified table '
                'and schema names.'
            )
        query = SQL(_phrasebook.gets('srid')).format(
            table=Literal(table_name),
            schema=Literal(schema_name),
            geomcol=Literal(_geometry_column)
        )
        return execute_scalar(cnx=cnx, query=query)
    finally:
        if close:
            _cnx.close()
