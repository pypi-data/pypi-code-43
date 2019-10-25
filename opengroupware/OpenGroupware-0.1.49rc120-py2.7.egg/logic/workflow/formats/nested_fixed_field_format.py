#
# Copyright (c) 2017, 2018
#  Adam Tauno Williams <awilliam@whitemice.org>
#  Contributions by Adam Seskunas
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
from copy import deepcopy
from format import COILS_FORMAT_DESCRIPTION_OK, Format
from format import COILS_FORMAT_DESCRIPTION_INCOMPLETE
from line_oriented_format import LineOrientedFormat
from exception import RecordFormatException
from coils.core import NotImplementedException
from .simple_fixed_field_format import SimpleFixedFieldFormat, RowField


class NestedFixedFieldFormat(SimpleFixedFieldFormat):

    def __init__(self):
        LineOrientedFormat.__init__(self)

    def set_description(self, fd):
        code = LineOrientedFormat.set_description(
            self, fd, verify_fields=False,
        )
        if (code[0] != 0):
            return code

        errors = list()

        # global format attibutes
        self._index_field_start = self._definition.get('indexFieldStart', 1, )
        self._index_field_end = self._definition.get('indexFieldEnd', 1, )
        self._input_locale = self._definition.get('inputLocale', '')
        self._skip_unknown_types = self._definition.get(
            'skipUndefinedRecordTypes', False,
        )

        self._record_types = dict()
        for record_type in [x for x in self._definition['recordTypes']]:
            record_definition = deepcopy(
                self._definition['recordTypes'][record_type]
            )
            self._record_types[record_type] = record_definition
            # verify record type fields
            for field in record_definition['fields']:
                if ('static' not in field):
                    """
                    Non-static-value fields must have a "start" and
                    "end" attribute.
                    """
                    if (('start' not in field) or ('end' not in field)):
                        errors.append(
                            '{0}:Field: <{1}> is missing start/end positition'
                            .format(record_type, field['name'], )
                        )
            if ('recordLength' not in record_definition):
                errors.append(
                    '{0}:RecordLength missing from description'
                    .format(record_type, )
                )
            elif (record_definition['recordLength'] is None):
                errors.append(
                    '{0}:RecordLength is not defined'.format(record_type, )
                )

        if errors:
            return (COILS_FORMAT_DESCRIPTION_INCOMPLETE, '\n'.join(errors))

        return (COILS_FORMAT_DESCRIPTION_OK, 'OK')

    @property
    def mimetype(self):
        return 'text/plain'

    def process_record_in(self, record):
        date_format = None
        row = list()

        self.in_counter = self.in_counter + 1
        if (self.in_counter <= self._skip_lines):
            self.log.debug('skipped initial line {0}'.format(self.in_counter))
            return

        if ((record[0:1] == '#') and (self._skip_comment)):
            self.log.debug('skipped commented line{0}'.format(self.in_counter))
            return

        record = ''.join(
            [c for c in record
             if ((127 > ord(c) > 31) or ord(c) in self._allowed_ords)]
        )
        if ((len(record) == 0) and (self._skip_blanks)):
            self.log.debug('skipped blank line {0}'.format(self.in_counter))
            return

        record_type = record[self._index_field_start - 1:self._index_field_end]
        record_type = record_type.strip()
        record_format = self._record_types.get(record_type, None)
        if record_format is None:
            if not self._skip_unknown_types:
                """ raise exception due to unknown record type """
                raise RecordFormatException(
                    'Record {0} has undefined record type: "{1}"'
                    .format(self.in_counter, record_type, )
                )
            else:
                """ ignore line of unknown record type """
                return

        for field in record_format.get('fields'):
            tmp = RowField(
                name=field['name'],
                kind=field.get('kind', 'string'),
                is_key=(str(field.get('key', 'false')).lower() == 'true'),
                value=field.get('static', None),
            )

            if tmp.value is None:
                try:
                    value = record[(field['start'] - 1):(field['end'])]
                    if tmp.kind in ('integer', 'float', 'ifloat', ):
                        tmp.value = self.process_numeric_value(
                            divisor=field.get('divisor', 1),
                            floor=field.get('floor', None),
                            cieling=field.get('cieling', None),
                            sign=field.get('sign', 'u'),
                            kind=tmp.kind,
                            value=value,
                        )
                    elif tmp.kind in ('date', ):
                        date_format = field.get('format', '%Y-%m-%d')
                        if value:
                            tmp.value = Format.Reformat_Date_String(
                                value, date_format, '%Y-%m-%d',
                            )
                        else:
                            tmp.value = None
                    elif tmp.kind in ('datetime', ):
                        date_format = field.get('format', '%Y-%m-%d %H:%M:%S')
                        if value:
                            tmp.value = Format.Reformat_Date_String(
                                value, date_format, '%Y-%m-%d %H:%M:%S',
                            )
                        else:
                            tmp.value = None
                    else:
                        # Default string type
                        if field.get('strip', False):
                            value = value.strip()
                        tmp.value = value
                except ValueError, e:
                    if tmp.kind in ('date', 'datetime', ):
                        message = (
                            'Value error converting value \"{0}\" to '
                            'type \"{1}\" for attribute \"{2}\" using '
                            'format "{3}".'
                            .format(value, tmp.kind, tmp.name, date_format, )
                        )
                    else:
                        message = (
                            'Value error converting value \"{0}\" to '
                            'type \"{1}\" for attribute \"{2}\".'
                            .format(value, tmp.kind, tmp.name, )
                        )
                    self.log.warn(message)
                    raise RecordFormatException(message, e)
            row.append(tmp)
        # RENDER ROW

        with self.xml.container(
            'row', attrs={
                'id': unicode(self.in_counter),
                'recordType': record_type,
            }
        ) as xml:
            for tmp in row:
                if tmp.kind is None:
                    raise RecordFormatException(
                        'kind is None writing record#{0} field "{1}" '
                        'in recordType#{2}'
                        .format(self.in_counter, tmp.name, record_type, )
                    )
                tmp.is_key = 'true' if tmp.is_key else 'false'
                if tmp.is_null:
                    xml.element(
                        tmp.name,
                        attrs={
                            'dataType': tmp.kind,
                            'isNull': 'true',
                            'isPrimaryKey': tmp.is_key,
                        }
                    )
                else:
                    xml.element(
                        tmp.name,
                        text=unicode(tmp.value),
                        attrs={
                            'dataType': tmp.kind,
                            'isNull': 'false',
                            'isPrimaryKey': tmp.is_key,
                        },
                    )

    def process_record_out(self, record):
        """ TODO: implement record out for nested record types"""
        raise NotImplementedException(
            'NestedFixedFieldFormat output not implemented'
        )
