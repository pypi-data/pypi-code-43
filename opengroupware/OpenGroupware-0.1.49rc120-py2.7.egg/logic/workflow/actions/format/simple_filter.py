#
# Copyright (c) 2010, 2013, 2015
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
import re
from coils.core import StandardXML, CoilsException
from coils.core.logic import ActionCommand


class SimpleFilter(ActionCommand):
    __domain__ = "action"
    __operation__ = "simple-filter"
    __aliases__ = ['simpleFilter', 'simpleFilterAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    def do_action(self):
        self._row_in = 0
        self._row_out = 0
        try:
            StandardXML.Filter_Rows(
                self._rfile,
                self._wfile,
                callback=self.callback
            )
        finally:
            self.log_message(
                u'\n  Rows input = {0}, Rows output = {1}'
                .format(self._row_in, self._row_out, ),
                category='info',
            )

    def _callback_equals(self, value):
        return (value == self._compare_value)

    def _callback_not_equals(self, value):
        return not(value == self._compare_value)

    def _callback_in(self, value):
        return (value in self._compare_value)

    def _callback_regex(self, value):
        if value:
            return self._compare_value.match(value)
        return False

    def callback(self, row):
        self._row_in += 1
        keys, fields = StandardXML.Parse_Row(row)
        # Get field value from row
        result = True
        for field_name in self._field_name:
            if field_name in keys:
                tmp = keys[field_name]
            elif field_name in fields:
                tmp = fields[field_name]
            else:
                raise CoilsException(
                    'Field {0} not found in input record.'
                    .format(field_name, )
                )
            # Compare Values
            result = (self._expression_callback(tmp) and result)
            if not result:
                break

        if self._keep_match and result:
            self._row_out += 1
            return True
        elif (not self._keep_match) and (not result):
            self._row_out += 1
            return True
        return False

    def parse_action_parameters(self):

        self._field_name = self._params.get('fieldName', None)
        if self._field_name is None:
            raise CoilsException('No field name specified for comparison.')
        self._field_name = [x.strip() for x in self._field_name.split(',')]


        self._compare_value = self._params.get('compareValue', None)
        if self._compare_value is None:
            raise CoilsException('No comparison value specified')

        action = self._params.get('action', 'KEEP').upper()
        if action == 'KEEP':
            self._keep_match = True
        elif action == 'DISCARD':
            self._keep_match = False
        else:
            raise CoilsException(
                'Undefined action "{0}" specified for simpleFilterAction'.
                format(action, )
            )

        cast_as = self._params.get('castAs', 'STRING').upper()

        expression = self._params.get('expression', 'EQUALS').upper()
        if expression in ('NOTEQUALS', 'EQUALS', ):
            if expression == 'EQUALS':
                self._expression_callback = self._callback_equals
            else:
                self._expression_callback = self._callback_not_equals
            if cast_as == 'INTEGER':
                self._compare_value = int(self._compare_value)
            elif cast_as == 'FLOAT':
                self._compare_value = float(self._compare_value)
            elif cast_as in ('STRING', 'UNICODE', ):
                self._compare_value = unicode(self._compare_value)
        elif expression == 'IN':
            self._compare_value = self._compare_value.split(',')
            if cast_as == 'INTEGER':
                self._compare_value = [int(x) for x in self._compare_value]
            elif cast_as == 'FLOAT':
                self._compare_value = [float(x) for x in self._compare_value]
            elif cast_as in ('STRING', 'UNICODE', ):
                self._compare_value = [unicode(x) for x in self._compare_value]
            self._expression_callback = self._callback_in
        elif expression == 'REGEXP':
            self._expression_callback = self._callback_regex
            self._compare_value = re.compile(self._compare_value)
        else:
            raise CoilsException(
                'Unknown comparision expression: "{0}", must be one '
                'of EQUALS, NOTEQUALS, IN, or REGEX.'
                .format(expression, )
            )
