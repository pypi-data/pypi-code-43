#
# Copyright (c) 2011, 2012, 2014, 2016
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
from coils.core import CoilsException
from table import Table


class StaticLookupTable(Table):
    # TODO: Add support for a default value and optional raiseError attribute
    # TODO: support for chained tables, static lookup failed over to SQL lookup

    def __repr__(self):
        return (
            '<StaticLookupTable name="{0}" count="{1}"/>'
            .format(self.name, len(self.c['values']), )
        )

    def set_description(self, description):
        self.c = description

        self._do_input_upper = False
        self._do_input_strip = False
        self._do_output_upper = False
        self._do_output_strip = False
        if self.c.get('doInputUpper', False):
            self._do_input_upper = True
        if self.c.get('doInputStrip', False):
            self._do_input_strip = True
        if self.c.get('doOutputUpper', False):
            self._do_output_upper = True
        if self.c.get('doOutputStrip', False):
            self._do_output_strip = True
        self._default_value = self.c.get('defaultValue', None)

        if 'values' not in self.c:
            raise CoilsException(
                'StaticLookupTable does not contain the required '
                '"values" attribute.'
            )
        if not isinstance(self.c['values'], dict):
            raise CoilsException(
                '"value" attribute of PresenceLookupTable is a "{0}"'
                ' and must be a "dict".'.format(type(self.c['values']), )
            )

    def lookup_value(self, *values):
        '''
        Prepare the input value and perform the look-up
        :param value:
        '''

        '''
        Tuples apparently do not expand like lists do;
        Ahh, Python and your crappy types.
        '''
        args = []
        for x in values:
            args.append(x)

        # Processing / Cleaning of input values
        if self._do_input_upper or self._do_input_strip:
            tmp = []
            for value in values:
                if isinstance(value, basestring):
                    if self._do_input_upper:
                        value = value.upper()
                    if self._do_input_strip:
                        value = value.strip()
                tmp.append(value)
            values = tmp
            tmp = None

        key = self.cache_key_from_values(values)
        result = self.c['values'].get(key, self._default_value)

        if isinstance(result, basestring):
            if self._do_output_upper:
                result = result.upper()
            if self._do_output_strip:
                result = result.strip()

        return result
