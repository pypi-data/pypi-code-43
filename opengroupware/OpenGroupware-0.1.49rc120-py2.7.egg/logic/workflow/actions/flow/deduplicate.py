#
# Copyright (c) 2019
#   Adam Tauno Williams <awilliam@whitemice.org>
#
# License: MIT/X11
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
from coils.core.logic import ActionCommand
from coils.core import StandardXML, CoilsException

LIST_CLASS = None
try:
    from blist import blist
    LIST_CLASS = blist
except:
    LIST_CLASS = list


class DeduplicateSXMLAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "standardxml-deduplication"
    __aliases__ = [
        'standardXMLDeduplication', 'standardXMLDeduplicationAction',
    ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'application/xml'

    def callback(self, row):
        key_strings = list()
        self._row_in += 1
        keys, fields = StandardXML.Parse_Row(row)

        if not (self._row_in % 8192):
            self.log_message(
                '{0} rows processed, found {1} keys'
                .format(self._row_in, len(self._key_buffer), ),
                category='debug',
            )
            self.gong()

        for field_name in self._key_fields:

            if field_name in keys:
                key_strings.append(str(keys[field_name]))
            elif field_name in fields:
                key_strings.append(str(fields[field_name]))
            else:
                raise CoilsException(
                    'Field {0} not found in input record.'
                    .format(field_name, )
                )  # field not found!

            key_string = chr(0x1c).join(key_strings)
            if (key_string in self._key_buffer):
                return False

            self._key_buffer.append(key_string)
            self._row_out += 1

            return True

    def do_action(self):
        self._key_buffer = LIST_CLASS()
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

    def parse_action_parameters(self):

        self._key_fields = [
            x.strip() for x in
            self.process_label_substitutions(
                self.action_parameters.get('keys')
            ).split(',')
        ]

    def do_epilogue(self):
        pass
