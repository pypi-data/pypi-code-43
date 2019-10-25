#
# Copyright (c) 2017, 2018
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
# THE SOFTWARE
#
import csv
from copy import deepcopy
from base64 import b64encode
from coils.foundation import StandardXML
from coils.core import CoilsException
from coils.foundation.api import elementflow
from format import COILS_FORMAT_DESCRIPTION_OK, Format
from line_oriented_format import LineOrientedFormat
from exception import RecordFormatException
from format import COILS_FORMAT_DESCRIPTION_INCOMPLETE


class RecordFieldEncodingException(RecordFormatException):
    pass


class Peekaboo(object):
    """
    Wrapper around the input stream; initially this was used for the purpose
    of enabling error reporting and to capture the input record on a failed
    unit.  Subsequently the Escaped End Quote hack was added, in the future
    additional Peekaboo layer hacks are expected.

    The Escaped End Quote hack, or EEQ, deals with having escape characters
    as the last value in a field, this breaks the record parsing as the
    quoting will continue to include the next field like "STUART H\","123" -
    this will be '''STUART H",'''.  Technically this is correct, but it may
    be the result of a lame file writer - the application IQ Report Writer is
    one application known to produce these broken files.  This hack, if enabled
    will replace the sequence {escapeChar}{quoteChar}{delimiterChar} with the
    sequence {quoteChar}{delimiterChar}; essentially removing the {escapeChar}.
    The {escapeChar} will continue to serve its expected purpose otherwise, it
    will only be removed when immediately followed by the specified quote
    character and delimiter.  Another option, depending on the file writer, is
    to more simply specify no escape character.  The correct approach depends
    on the application creating the file.
    """
    __slots__ = ('_h', '_d', '_c', '_enable_hack_eeq', )

    def __init__(
        self, handle,
        quote_char=None,
        escape_char=None,
        delimiter=None,
        enable_escaped_end_quote_hack=False,
    ):
        self._h = handle
        self._h.seek(0)
        self._c = None
        self._enable_hack_eeq = None
        if enable_escaped_end_quote_hack:
            self._enable_hack_eeq = (
                '{0}{1}{2}'.format(escape_char, quote_char, delimiter, ),
                '{0}{1}'.format(quote_char, delimiter, )
            )

    def __iter__(self):
        for row in iter(self._h):
            self._c = row
            if self._c and self._enable_hack_eeq:
                self._c = self._c.replace(
                    self._enable_hack_eeq[0],
                    self._enable_hack_eeq[1],
                )
            yield self._c

    @property
    def current(self):
        return self._c


class RowField(object):
    """
    Convenient wrapper for the a row field. This makes syntax less cluttered
    than just using a dictionary and streamlines the handling of the isNULL
    attribute.
    """
    __slots__ = ('value', 'kind', 'is_key', 'name', 'prefix', 'suffix', )

    def __init__(self, name, value, kind, is_key, prefix, suffix):
        self.name = name
        self.value = value
        self.kind = kind
        self.is_key = is_key
        self.prefix = prefix
        self.suffix = suffix

    @property
    def is_null(self):
        if self.value is None:
            return True
        return False


class NestedDelimitedFieldFormat(LineOrientedFormat):

    def __init__(self):
        self._description_index = {}
        LineOrientedFormat.__init__(self)

    def _make_value_to_key(self, value):
        """
        make the value into a record format key, this makes it a unicode
        string value, leading and trailing whitespace stripped, and any
        internal spaces replaced with underscore.  All record format keys
        begin with an underscore value.  For example an input value of " 01"
        will become "_01"
        """
        if not isinstance(value, basestring):
            value = unicode(value)
        value = value.strip()
        value = value.replace(' ', '_')
        return '_{0}'.format(value, )

    def set_description(self, fd, verify_fields=False):

        print verify_fields
        code = LineOrientedFormat.set_description(
            self, fd, verify_fields=verify_fields,
        )
        if not (code[0] == 0):
            return code

        '''
        TODO: allow quote character and delimiter to be specified as
        and ordinal values
        '''
        self._delimiter = str(self._definition.get('delimiter', ','))
        if (len(self._delimiter) > 1):
            self.log.debug(
                'Converting delimiter from hexidecimal value "{0}"'
                .format(self._delimiter, )
            )
            self._delimiter = chr(int(self._delimiter, 16))
        self.log.debug('Value delimiter is "{0}"'.format(self._delimiter))
        self._quotechar = str(self._definition.get('quote', '"'))
        self._doublequote = bool(
            self._definition.get('doubleQuote', False)
        )

        self._escape_char = self._definition.get(
            'escapeCharacter', '\\'
        )

        self._quote_strategy = self._definition.get(
            'quotingStrategy', 'minimal'
        )
        if self._quote_strategy == 'nonnumeric':
            self._quote_strategy = csv.QUOTE_NONNUMERIC
        elif self._quote_strategy == 'all':
            self._quote_strategy = csv.QUOTE_ALL
        elif self._quote_strategy == 'none':
            self._quote_strategy = csv.QUOTE_NONE
        else:
            self._quote_strategy = csv.QUOTE_MINIMAL

        self._enable_hack_eeq = self._definition.get(
            'enableEscapedEndQuoteHack', False,
        )

        self._index_field = self._definition.get('indexField', 0, )

        self._record_types = dict()
        for record_type in [x for x in self._definition['recordTypes']]:
            record_definition = deepcopy(
                self._definition['recordTypes'][record_type]
            )
            for field in record_definition:
                if not ('kind' in field):
                    return (
                        COILS_FORMAT_DESCRIPTION_INCOMPLETE,
                        'Incomplete Description: kind missing from <{0}> '
                        'field definition for recordType "{1}"'
                        .format(field['name'], record_type, )
                    )
            self._record_types[record_type] = record_definition

        return (COILS_FORMAT_DESCRIPTION_OK, 'OK')

    @property
    def mimetype(self):
        return 'text/plain'

    def process_in(self, rfile, wfile):

        # TODO: Read quoting and delimiter from format definition
        self._input = rfile
        self._result = []

        self.xml = elementflow.xml(
            wfile,
            u'ResultSet',
            attrs={
                'className': self.__class__.__name__,
                'formatName': self.description.get('name'),
                'tableName': self.description.get('tableName', '_undefined_'),
            },
            indent=False,
        )

        wrapper = Peekaboo(
            handle=rfile,
            quote_char=self._quotechar,
            escape_char=self._escape_char,
            delimiter=self._delimiter,
            enable_escaped_end_quote_hack=self._enable_hack_eeq,
        )

        self.in_counter = 0

        with self.xml:
            for record in csv.reader(
                wrapper,
                delimiter=self._delimiter,
                quotechar=self._quotechar,
                doublequote=self._doublequote,
                escapechar=self._escape_char,
            ):
                try:
                    data = self.process_record_in(record)
                    self.pause(self.in_counter)
                except RecordFormatException as exc:
                    self.reject(wrapper.current, str(exc))
                    self.log.warn(
                        'Record format exception on record {0}: {1}'
                        .format(self.in_counter, unicode(record), )
                    )
                    if (self._discard_on_error):
                        self.log.info(
                            'Record {0} of input message dropped due to '
                            'format error'.format(self.in_counter, )
                        )
                    else:
                        raise exc
                except UnicodeDecodeError as exc:
                    self.reject(wrapper.current, str(exc))
                    data = b64encode(wrapper.current)

                    self.log.warn(
                        'Record format exception on record {0} due to '
                        'encoding: {1}'.format(
                            self.in_counter, data,
                        )
                    )
                    if self._discard_on_error:
                        self.log.info(
                            'Record {0} of input message dropped due to '
                            'encoding error'.format(self.in_counter, )
                        )
                    else:
                        raise exc

            self.set_record_counter(self.in_counter)
            return

    def process_record_in(self, record):

        row = list()

        self.in_counter += 1

        if (self.in_counter <= self._skip_lines):
            self.log.debug('skipped initial line {0}'.format(self.in_counter))
            return None
        if ((record[0:1] == '#') and (self._skip_comment)):
            self.log.debug('skipped commented line{0}'.format(self.in_counter))
            return None
        if ((len(record) == 0) and (self._skip_blanks)):
            self.log.debug('skipped blank line {0}'.format(self.in_counter))
            return None

        # DETERMINE RECORD TYPE
        try:
            record_type = str(record[self._index_field]).strip()
        except Exception as exc:
            self.log.error('Unable to evaluate recordType value')
            raise RecordFormatException()

        record_definition = self._record_types[record_type]
        if not(len(record) == len(record_definition)):
            raise RecordFormatException(
                'Input record {0} has {1} fields, definition of '
                'recordType "{2}" has {3} fields.'.format(
                    self.in_counter,
                    len(record),
                    record_type,
                    len(record_definition)
                )
            )

        for i in range(0, len(record_definition)):

            field = record_definition[i]

            if 'static' in field:
                value = str(field.get('static'))
            else:
                value = str(record[i])  # value should always be a string

            try:
                tmp = RowField(
                    name=field['name'],
                    kind=field.get('kind', 'string'),
                    is_key=(str(field.get('key', 'false')).lower() == 'true'),
                    prefix=field.get('prefix', None),
                    suffix=field.get('suffix', None),
                    value=value,
                )
            except IndexError:
                raise RecordFormatException(
                    'Attempt to read beyond end of record in record {0}, '
                    '{1} fields defined, {2} fields in record'
                    .format(
                        self.in_counter,
                        len(self._definition.get('fields')),
                        len(record),
                    )
                )

            if (bool(field.get('discard', False))):
                continue

            try:
                if (field.get('strip', True)):
                    tmp.value = tmp.value.strip()
                if (field.get('upper', True)):
                    tmp.value = tmp.value.upper()
                if (field['kind'] in ['date']):
                    if (len(tmp.value) > 0):
                        tmp.value = Format.Reformat_Date_String(
                            tmp.value, field['format'], '%Y-%m-%d'
                        )
                    else:
                        tmp.value = None
                elif (field['kind'] in ['datetime']):
                    if (len(tmp.value) > 0):
                        tmp.value = Format.Reformat_Date_String(
                            tmp.value, field['format'], '%Y-%m-%d %H:%M:%S'
                        )
                    else:
                        tmp.value = None
                elif (field['kind'] in ['integer', 'float', 'ifloat']):
                    # Numeric types
                    divisor = field.get('divisor', 1)
                    floor = field.get('floor', None)
                    cieling = field.get('cieling', None)
                    if (field.get('sign', '') == 'a'):
                        sign = tmp.value[-1:]  # Take last character as sign
                        tmp.value = tmp.value[:-1]  # Drop last character
                    elif (field.get('sign', '') == 'b'):
                        sign = tmp.value[0:1]  # Take first character as sign
                        tmp.value = tmp.value[1:]  # Drop first character
                    else:
                        sign = '+'
                    '''
                    self.log.debug(
                        'sign character for field {0} is {1}'
                        .format(field['name'], sign)
                    )
                    '''
                    if (sign == '+'):
                        sign = 1
                    else:
                        sign = -1
                    if (len(tmp.value) == 0):
                        tmp.value = field.get('default', None)
                    elif (field['kind'] == 'integer'):
                        tmp.value = (int(float(tmp.value)) * int(sign))
                        if (floor is not None):
                            floor = int(floor)
                        if (cieling is not None):
                            cieling = int(cieling)
                        if (divisor != 1):
                            tmp.value = tmp.value / int(divisor)
                    else:
                        tmp.value = (float(tmp.value) * float(sign))
                        if (floor is not None):
                            floor = float(floor)
                        if (cieling is not None):
                            cieling = float(cieling)
                        if (divisor != 1):
                            tmp.value = tmp.value / float(field['divisor'])
                    if (tmp.value is not None):
                        if (floor is not None) and (tmp.value < floor):
                            message = 'Value {0} below floor {1}'.format(
                                tmp.value, floor,
                            )
                            self.log.warn(message)
                            raise ValueError(message)
                        if (cieling is not None) and (tmp.value > cieling):
                            message = 'Value {0} above cieling {1}'.format(
                                tmp.value, cieling,
                            )
                            self.log.warn(message)
                            raise ValueError(message)
                else:
                    if (len(tmp.value) == 0):
                        tmp.value = field.get('default', None)
                    if (tmp.value is not None):
                        try:
                            tmp.value = tmp.value.encode("utf-8")
                            tmp.value = self.encode_text(tmp.value)
                        except Exception as exc:
                            raise RecordFieldEncodingException(
                                'Code-page error encoding field "{0}" '
                                'for row {1}; base64 encoded value is {2}'
                                .format(
                                    tmp.name,
                                    self.in_counter,
                                    b64encode(tmp.value)
                                ),
                                exc,
                            )
                    if tmp.prefix:
                        # remove prefix, if defined
                        tmp.value = tmp.value[len(tmp.prefix):]
                    if tmp.suffix:
                        # remove suffix, if defined
                        tmp.value = tmp.value[:-len(tmp.suffix)]
            except ValueError as exc:
                message = (
                    'Value error converting value "{0}" to type "{1}" '
                    'for attribute "{2}".'
                    .format(tmp.value, tmp.kind, tmp.name, )
                )
                self.log.warn(message)
                raise RecordFormatException(message, exc)
            row.append(tmp)
            tmp = None

        with self.xml.container(
            'row',
            attrs={
                'recordType': record_type,
                'id': unicode(self.in_counter),
            }
        ) as xml:
            for tmp in row:
                tmp.is_key = 'true' if tmp.is_key else 'false'
                if tmp.is_null:
                    xml.element(
                        tmp.name,
                        attrs={
                            'dataType': tmp.kind,
                            'isNull':   'true',
                            'isPrimaryKey': tmp.is_key,
                        }
                    )
                else:
                    xml.element(
                        tmp.name,
                        text=unicode(tmp.value),
                        attrs={
                            'dataType':      tmp.kind,
                            'isNull':       'false',
                            'isPrimaryKey': tmp.is_key,
                        },
                    )

    def process_out(self, rfile, wfile):

        record_count = 0
        writer = csv.writer(
            wfile,
            delimiter=self._delimiter,
            quotechar=self._quotechar,
            doublequote=self._doublequote,
            quoting=self._quote_strategy,
            escapechar=self._escape_char,
        )

        fields = self._definition.get('fields')
        for keys, fields, in StandardXML.Read_Rows(rfile):
            record_count += 1
            record = list()
            for i in range(0, len(self._definition.get('fields'))):
                field = self._definition.get('fields')[i]
                field_name = field['name']
                if (bool(field.get('discard', False))):
                    continue

                if field_name in keys:
                    value = keys.get(field_name)
                elif field_name in fields:
                    value = fields.get(field_name)
                else:
                    try:
                        value = field['static']
                    except KeyError:
                        raise CoilsException(
                            'Required field "{0}" missing from record {1} '
                            'for writeAction of format "{2}"'
                            .format(
                                field_name,
                                record_count,
                                self.get_name(),
                            )
                        )

                if value is None:
                    record.append('')
                elif field['kind'] in ('date', 'datetime', ):
                    if field['kind'] == 'date':
                        out_format = '%Y-%m-%d'
                    else:
                        out_format = '%Y-%m-%d %H:%M:%S'
                    out_format = field.get('format', out_format)
                    record.append(unicode(value.strftime(out_format)))
                elif field['kind'] in ('integer', 'float', 'ifloat', ):
                    # TODO: Implement support for "sign"
                    value = float(value)
                    if field.get('divisor', 1) != 1:
                        value = value * field.get('divisor')
                    if field['kind'] in ('integer', 'ifloat', ):
                        record.append(long(value))
                    elif field['kind'] in ('float', ):
                        record.append(value)
                    elif field['kind'] in ('string', ):
                        if field.get('prefix', None):
                            value = '{0}{1}'.format(field['prefix'], value)
                        if field.get('suffix', None):
                            value = '{0}{1}'.format(value, field['suffix'])
                        record.append(unicode(value))

            writer.writerow(record)

            record = None

        writer = None
        wfile.flush()

        self.set_record_counter(record_count)
