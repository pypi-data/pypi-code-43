#
# Copyright (c) 2017
#  Adam Tauno Williams <awilliam@whitemice.org>
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN#
# THE SOFTWARE
#
import pymssql
from sql_connection import SQLConnection

"""
    WARNING: USE ODBC AND MICROSOFT'S LINUX DRIVER!!!!  The FreeTDS
    which is the foundation of pymssql is winding down.  The ODBC driver
    is the support method for accessing an M$-SQL server from LINUX.
      - 2017-11-08

Record field types used in cursor.description do not appear to be
"officially" documented.  On StackOverflow there is an enumeration of:
  1 : STRING type
  2 : BINARY type
  3 : NUMBER type
  4 : DATETIME type
  5 : ROWID type
 https://stackoverflow.com/questions/33335489/how-to-get-column-data-types-from-pymssql
 which appear to simply be the DBAPI type enumeration
 https://cewing.github.io/training.codefellows/lectures/day21/intro_to_dbapi2.html#data-types-constructors
 That is pretty sad, but it is wha it is.  This means that pymssql treats
 booleans as numbers and UUIDs as binary.

 However testing shows the type codes are:
  1 : string
  2: BINARY (ROWID?)
  3: integer
  4: datetime
  5: float

  Looking at the FreeTDS project I find -
    Add suport for date, time and datetime2
    https://github.com/pymssql/pymssql/pull/398
    merged to master on 2016-02-23

  Do we care about antique versions of SQL-Server? No, at least not unless
  someone complains.  The type datetime2 was introduced in SQL Server 2008 -
  that will be TEN YEARS OLD in just a couple months [making this note on
  2017-11-03].  That seems like a long enough support window; certainly
  anything older is out of the OEM's support window.

  It is possible to see the underlying FreeTDS from via the pymssq module
    >>> pymssql.get_dbversion()
    'freetds v0.95'
  It is **VERY** important to have a current FreeTDS to get everything tp
  work in a sane/coherent manner with all the features one expectsion from
  a 2008 server.  In light of this

"""


class MSSQLConnection(SQLConnection):

    def __init__(self, params):
        if 'database' in params:
            self._db = pymssql.connect(
                params.get('hostname'), params.get('username'),
                params.get('password'), params.get('database'),
            )
        else:
            # no database specified, using default
            self._db = pymssql.connect(
                params.get('hostname'), params.get('username'),
                params.get('password'),
            )

    def connect(self):
        return self._db

    def cursor(self, **params):
        return self._db.cursor(**params)

    def get_type_from_code(string, code):
        if (code == 1):
            return 'string'
        elif (code == 2):
            return 'binary'
        elif (code == 3):
            return 'integer'
        elif (code == 4):
            return 'datetime'
        elif (code == 5):
            # ROWID, but really it is usually Decimal
            return 'float'
        else:
            return 'unknown'
