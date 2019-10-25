#
# Copyright (c) 2010, 2012, 2013, 2016, 2018, 2019
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
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
import base64
import time
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from utility import sql_connect

"""
Dealing with incoming values with whack-a-do encoding; we really cannot
trust the backend database, which could be anything.

>>> text = '1/4-20\xc3\x831  ss carriage bolt'
>>> unicode(text)
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
UnicodeDecodeError: 'ascii' codec can't decode byte 0xc3 in position 6:
  ordinal not in range(128)
>>> base64.encodestring(text)
'MS80LTIww4MxICBzcyBjYXJyaWFnZSBib2x0\n'
>>> buf = buffer(text)
>>> buf
<read-only buffer for 0x7fda78978930, size -1, offset 0 at 0x7fda789789f0>
>>> base64.encodestring(buf)
'MS80LTIww4MxICBzcyBjYXJyaWFnZSBib2x0\n'
"""

FIELD_OUT_FORMAT = (
    '<{0} dataType=\"{1}\" isPrimaryKey=\"{2}\" '
    'isBase64=\"{3}\" isNull=\"false\">{4}</{0}>'
)
NULL_FIELD_OUT_FORMAT = \
    '<{0} dataType=\"{1}\" isPrimaryKey=\"false\" isNull=\"true\"/>'


class SelectAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "sql-select"
    __aliases__ = ['sqlSelectAction', 'sqlSelect', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_encoding(self):
        return 'utf-8'

    @property
    def result_mimetype(self):
        return 'application/xml'

    """
    db object must have methods:
        cursor(), close(), get_type_from_code(type_txt)
    cursor object must have methods: fetchone(), close(), execute(query_txt)
    cursor object must have properties: description
    """

    @property
    def default_arraysize(self):
        return 65535

    def _open_cursor(self):
        db = sql_connect(self._source)
        self.log_message(
            message='Connected to datasource "{0}"'.format(self._source, ),
            category='info',
        )
        cursor = db.cursor()
        if hasattr(cursor, 'arraysize'):
            # Some primitive drivers do not have an arraysize property!!!
            cursor.arraysize = self.default_arraysize
        return db, cursor

    def _fetch_row(self, cursor):
        return cursor.fetchone()

    def _yield_row(self, cursor):
        rows = cursor.fetchmany()
        while rows:
            for row in rows:
                yield row
            rows = cursor.fetchmany()

    def do_action(self):

        self.log_message(
            message='Default string for unicode errors: {0}'.format(self._unicode_default, ),
            category='debug',
        )

        db, cursor = self._open_cursor()

        self.log_message(
            message='QUERY: {0}'.format(self._query, ), category='debug',
        )
        x_ = time.time()
        cursor.execute(self._query)  # execute query
        self.log_message(
            message='query execution consumed {0}s'.format(time.time() - x_, ),
            category='debug',
        )
        x_ = None

        self.wfile.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        self.wfile.write(
            u'<ResultSet formatName=\"_sqlselect_\" '
            'className=\"\" tableName=\"{0}\">'.
            format(self._table, )
        )

        """ description will be list of columns: field# = (name, type) """
        description = []

        counter = 0
        record_length = 0
        for record in self._yield_row(cursor):

            if counter == 0:
                record_length = len(record)
                # build description before processing first row
                for x in cursor.description:
                    # tuple format: name, type-string
                    description.append(
                        (
                            x[0].lower(),
                            db.get_type_from_code(x[1]).lower(),
                        )
                    )

            # implement row fetch limit
            if (self._limit > 0) and (counter > self._limit):
                break

            counter += 1
            self.wfile.write(u'<row id="{0}">'.format(counter, ))  # start row

            for i in range(0, record_length):

                is_base64 = False
                name, kind = description[i]
                is_key = (name in self._keys)
                value = record[i]

                if kind == 'binary':
                    is_base64 = True
                    # what if the value is not a string?
                    value = base64.encodestring(value).strip()
                elif ((kind == 'string') and (value is not None)):
                    """
                    The string value may be a buffer depending on the origin -
                    sources such as a TEXT (BLOB) in Informix will not be
                    basestring but will be a buffer object.  This buffer
                    object needs to be read as a unicode string so that it
                    can be XML encoded/escaped.
                    """
                    # make value into a UTF-8
                    if isinstance(value, basestring):
                        try:
                            # TODO: we should make the 'ignore' optional
                            value = value.\
                                decode(self._codepage).\
                                encode('utf-8', 'ignore')
                        except Exception as exc:
                            # HACK: Unicode Default Value
                            if self._unicode_default is not None:
                                value = self._unicode_default
                                message = (
                                    'Unable to encode value of field "{0}" of '
                                    'row {1} to UTF-8 string, falling back to '
                                    'default string value'.
                                    format(name, counter, )
                                )
                                self.log_message(
                                    message=message, category='info',
                                )
                            else:
                                """
                                try to make the unicode string into base64
                                WARN: this is a HACK and probably doesn't work
                                """
                                message = (
                                    'Unable to encode value of field "{0}" of '
                                    'row {1} to UTF-8 string, falling back to '
                                    'base64 encoding'.
                                    format(name, counter, )
                                )
                                self.log.error(message)
                                self.log.exception(exc)
                                self.log_message(
                                    message=message, category='info',
                                )
                                is_base64 = True
                                value = base64.encodestring(value).strip()
                    else:
                        # String data but not a string type

                        """
                        TODO: is this useful?  or was it just for debugging
                          at some point - notably it does not DO antying

                        message = (
                            'casting to unicode a non-string of type {1} for '
                            'field "{0}" of row {2}'
                            .format(name, type(value), counter, )
                        )
                        self.log.warning(message)
                        self.log_message(
                            message=message, category='info',
                        )
                        """

                        # make value a unicode string
                        text = None
                        try:
                            text = unicode(value)
                        except UnicodeDecodeError as exc:
                            self.log.error(
                                'Unable to cast value field "{0}" to UTF-8 '
                                'string; falling back to base64 encoding'
                                .format(name, )
                            )
                            self.log.exception(exc)
                            is_base64 = True
                            value = base64.encodestring(value).strip()
                        else:
                            value = text

                    # Perform XML encoding
                    if not is_base64:
                        value = self.encode_text(value, encoding='utf-8')

                if value is None:
                    # write NULL value, no value!
                    if is_key:
                        raise CoilsException(
                            'NULL Primary Key value detected.'
                        )
                    self.wfile.write(
                        NULL_FIELD_OUT_FORMAT.format(name, kind, )
                    )
                else:
                    # write a materialized value
                    try:
                        self.wfile.write(
                            FIELD_OUT_FORMAT.format(
                                name, kind,
                                'true' if is_key else 'false',  # key
                                'true' if is_base64 else 'false',  # base64
                                value,
                            )
                        )
                    except UnicodeEncodeError as exc:
                        # YES!  Log the golram value causing the issue
                        self.log_message(
                            message='encodeing error with field "{0} having value {1}'.format(  # noqa
                                name,
                                value.encode('base64').strip(),
                            ), category='error',
                        )
                        raise exc

            self.wfile.write(u'</row>')

            if not (counter % 8192):
                self.gong()

        self.wfile.write(u'</ResultSet>')
        description = None
        cursor.close()
        db.close()
        self.log_message(
            message=(
                'Retrieved {0} records from database connection'
                .format(counter, )
            ),
            category='debug',
        )

    def parse_action_parameters(self):
        self._source = self.action_parameters.get('dataSource', None)
        self._query = self.action_parameters.get('queryText', None)
        self._limit = int(self.action_parameters.get('limit', 150))
        self._table = self.action_parameters.get('tableName', '_undefined_')
        self._keys = self.action_parameters.get('primaryKeys', '').split(',')
        self._unicode_default = self.action_parameters.get('defaultString', None)  # noqa
        self._codepage = self.action_parameters.get('codepage', 'utf-8')
        if (self._source is None):
            raise CoilsException('No source defined for selectAction')
        if (self._query is None):
            raise CoilsException('No query defined for selectAction')
        else:
            self._query = self.decode_text(self._query)
            self._query = self.process_label_substitutions(self._query)

    def do_epilogue(self):
        pass
