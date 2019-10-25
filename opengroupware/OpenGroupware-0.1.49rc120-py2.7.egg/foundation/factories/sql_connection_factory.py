#
# Copyright (c) 2010, 2012, 2014, 2017, 2019
#   Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE
#
import logging
from coils.foundation.defaultsmanager import ServerDefaultsManager


class SQLConnectionFactory(object):
    _classes = None

    @staticmethod
    def Init():
        log = logging.getLogger('OIE')
        SQLConnectionFactory._classes = {}

        # Informix
        try:
            import informixdb
        except Exception as e:
            log.info('Unable to load Informix support')
            log.exception(e)
        else:
            log.info('Informix support loaded')
            from informix_connection import InformixConnection
            SQLConnectionFactory._classes['informix'] = InformixConnection

        # PostgreSQL
        try:
            import psycopg2
        except:
            log.warning('Unable to load PostgreSQL support')
        else:
            log.info('PostgreSQL support loaded')
            from postgres_connection import PostgresConnection
            SQLConnectionFactory._classes['postgres'] = PostgresConnection

        # M$-SQL
        try:
            import pymssql
            if (pymssql.get_dbversion().startswith('freetds v0')):
                log.warning('pymssql module found, but FreeTDS version is obsolete')  # noqa
                log.warning('FreeTDS v1.0 or greated is required')
                raise Exception('Obsolete FreeTDS version')
        except:
            log.info('Unable to load Microsoft SQL-Server support')
        else:
            log.info('Microsoft SQL-Server support loaded')
            log.warning('Microsoft SQL-Server is deprecated - use ODBC')
            from mssql_connection import MSSQLConnection
            SQLConnectionFactory._classes['mssql'] = MSSQLConnection

        # ODBC
        try:
            import pyodbc
        except:
            log.info('Unable to load ODBC connectivity support')
        else:
            log.info('ODBC connectivity support loaded')
            from odbc_connection import ODBCConnection
            SQLConnectionFactory._classes['odbc'] = ODBCConnection

    @staticmethod
    def Connect(source):
        if (SQLConnectionFactory._classes is None):
            SQLConnectionFactory.Init()
        log = logging.getLogger('OIE')
        config = None
        if isinstance(source, basestring):
            """
            source is a string, so it is a reference to a defined SQL database
            connection from the OIESQLSources configuration directive
            """
            sd = ServerDefaultsManager()
            config = sd.default_as_dict('OIESQLSources')
            if (source in config):
                config = config.get(source)
            else:
                log.error('No source defined with name {0}'.format(source, ))
        elif isinstance(source, dict):
            """
            source is a dictionary - so we assume it is a database connection
            configuation.  this is intended primarily for testing.
            TODO: it may even be wise to only offer this functionality
            provided a given environment variable is set.
            """
            config = source

        try:
            driver = SQLConnectionFactory._classes.get(
                config.get('driver')
            )
            connection = driver(config)
        except Exception as exc:
            log.exception(exc)
            log.error(
                'Unable to provide connection to source name {0}'
                .format(source, )
            )
            return None
        else:
            return connection
