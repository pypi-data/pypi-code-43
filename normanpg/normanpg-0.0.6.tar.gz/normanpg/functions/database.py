#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 9/29/19
"""
.. currentmodule:: normanpg.functions.db
.. moduleauthor:: Pat Blair <pblair@geo-comm.com>

This module contains database-level functions.
"""
from urllib.parse import urlparse, ParseResult
from phrasebook import SqlPhrasebook
import psycopg2.extensions
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from psycopg2.sql import Literal, Identifier, SQL
from ..errors import NormanPgException
from ..pg import (
    connect, execute, execute_scalar,
    DEFAULT_ADMIN_DB
)

_PHRASEBOOK = SqlPhrasebook().load()


def parse_dbname(url: str) -> str:
    """
    Parse the database name from a connection URL.

    :param url: the URL
    :return: the database name
    """
    db: ParseResult = urlparse(url)
    dbname = db.path[1:]
    return dbname


def db_exists(
        url: str,
        dbname: str = None,
        admindb: str = DEFAULT_ADMIN_DB
) -> bool:
    """
    Does a given database on a Postgres instance exist?

    :param url: the database URL
    :param dbname: the name of the database to test
    :param admindb: the name of an existing (presumably the main) database
    :return: `True` if the database exists, otherwise `False`
    """
    # Figure out what database we're looking for.
    _dbname = dbname if dbname else parse_dbname(url)

    # Prepare the query.
    query = SQL(_PHRASEBOOK.gets('select_db_count')).format(
        dbname=Literal(_dbname)
    )
    # Create a connection to the administrative database.
    with connect(url=url, dbname=admindb) as cnx:
        # The query should return a count of the appearances of the database
        # name in an index table.
        count = execute_scalar(cnx=cnx, query=query)
        try:
            count = int(count)
        except ValueError:
            raise NormanPgException(
                f'The database returned a non-integer response: {count}'
            )
        # If the count is more than 1, there is something wrong with the result
        # (since it should be the number of databases with the given name).
        if count > 1:
            raise NormanPgException(
                f'The database returned an unexpected result: {count}'
            )
        # If the name appeared exactly one (1) time, the database exists.
        # Otherwise, it doesn't.
        return count == 1


def create_db(
        url: str,
        dbname: str,
        admindb: str = DEFAULT_ADMIN_DB
):
    """
    Create a database on a Postgres instance.

    :param url: the database URL
    :param dbname: the name of the database
    :param admindb: the name of an existing (presumably the main) database
    """
    # Figure out what database we're looking for.
    _dbname = dbname if dbname else parse_dbname(url)
    # Construct the query.
    query = SQL(_PHRASEBOOK.gets('create_db')).format(
        dbname=Identifier(_dbname)
    )
    # Let's create the database.
    with connect(url=url, dbname=admindb) as cnx:
        cnx.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        try:
            execute(cnx=cnx, query=query)
        except psycopg2.IntegrityError:
            raise


def create_extension(
        url: str,
        extension: str,
        dbname: str = None
):
    """
    Create (install) an extension in a database.

    :param url: the database URL
    :param extension: the name of an existing (presumably the main) database
    :param dbname: the name of the database
    """
    # Figure out what database we're looking for.
    _dbname = dbname if dbname else parse_dbname(url)
    # Construct the query.
    query = SQL(_PHRASEBOOK.gets('create_extension')).format(
        extension=SQL(extension)
    )
    # Create the extension.
    with connect(url=url, dbname=dbname) as cnx:
        execute(cnx=cnx, query=query)


def touch_db(
        url: str,
        dbname: str = None,
        admindb: str = DEFAULT_ADMIN_DB
):
    """
    Create a database if it does not already exist.

    :param url: the database URL
    :param dbname: the name of the database
    :param admindb: the name of an existing (presumably the main) database
    """
    # If the database already exists, we don't need to do anything further.
    if db_exists(url=url, dbname=dbname, admindb=admindb):
        return

    # Let's see what we got for the database name.
    _dbname = dbname if dbname else parse_dbname(url)

    # Now we can create it.
    create_db(url=url, dbname=_dbname, admindb=admindb)


def create_schema(
        url: str,
        schema: str,
        dbname: str = None
):
    """
    Create a schema in the database.

    :param url: the database URL
    :param schema: the name of the schema
    :param dbname: the name of the database
    """
    # Figure out what database we're looking for.
    _dbname = dbname if dbname else parse_dbname(url)
    # Construct the query.
    query = SQL(_PHRASEBOOK.gets('create_schema')).format(
        schema=SQL(schema)
    )
    # Create the schema.
    with connect(url=url, dbname=dbname) as cnx:
        execute(cnx=cnx, query=query)


def drop_schema(
        url: str,
        schema: str,
        dbname: str = None,
        cascade: bool = True
):
    """
    Drop a schema in the database.

    :param url: the database URL
    :param schema: the name of the schema
    :param dbname: the name of the database
    :param cascade: ``True`` to drop the schema even if it is not empty,
        otherwise the attempt fails
    """
    # Figure out what database we're looking for.
    _dbname = dbname if dbname else parse_dbname(url)
    # Construct the query.
    query = SQL(_PHRASEBOOK.gets('drop_schema')).format(
        schema=SQL(schema),
        cascade=SQL('CASCADE' if cascade else 'RESTRICT')
    )
    # Create the schema.
    with connect(url=url, dbname=dbname) as cnx:
        execute(cnx=cnx, query=query)
