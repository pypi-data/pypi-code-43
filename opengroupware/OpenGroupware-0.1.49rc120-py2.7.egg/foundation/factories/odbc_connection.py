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
import pyodbc
import decimal
import datetime
from sql_connection import SQLConnection


class ODBCConnection(SQLConnection):

    def __init__(self, params):
        self._db = pyodbc.connect(params.get('DSN'))

    def connect(self):
        return self._db

    def cursor(self, **params):
        return self._db.cursor(**params)

    def get_type_from_code(self, code):
        if code == unicode:
            return 'string'
        if code == str:
            return 'string'
        elif code == bool:
            return 'integer'  # TODO: does StandardXML need a BOOL type?
        elif code == int:
            return 'integer'
        elif code == datetime.datetime:
            return 'datetime'
        elif code == decimal.Decimal:
            return 'float'
        else:
            return 'unknown'
