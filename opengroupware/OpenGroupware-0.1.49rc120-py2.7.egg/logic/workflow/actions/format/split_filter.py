#
# Copyright (c) 2019
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
import shutil
import zipfile
from tempfile import NamedTemporaryFile
from coils.core import StandardXML, CoilsException
from coils.foundation import BLOBManager
from coils.core.logic import ActionCommand


class SplitFilterAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "split-filter"
    __aliases__ = ['splitFilter', 'splitFilterAction', ]

    def __init__(self):
        ActionCommand.__init__(self)
        self._chunk_count = 0
        self._anchor_value = None

    @property
    def result_mimetype(self):
        return u'application/zip'

    def do_action(self):
        counter = 0
        chunks = list()
        self._row_in = 0
        self._row_out = 0
        table_name, format_name, format_class = \
            StandardXML.Read_ResultSet_Metadata(self.rfile)
        try:
            for fk, ff, fm, in StandardXML.Read_Rows(
                self.rfile, with_metadata=True
            ):
                self._row_in += 1
                counter += 1
                # metadata : row_operation, record_type, type_map
                if not chunks:
                    # start an initial chunk
                    self._set_anchor(fk, ff, fm, )
                    chunks.append(
                        self._start_chunk(
                            table_name, format_name, format_class,
                        )
                    )
                elif self._new_chunk(fk, ff, fm, ):
                    self.log_message(
                        'wrote {0} rows to chunk {1}'
                        .format((counter - 1), len(chunks), ),
                        category='debug',
                    )
                    counter = 1
                    # close existing chunk
                    self._end_chunk(chunks[-1])
                    # start a new chunk
                    chunks.append(
                        self._start_chunk(
                            table_name, format_name, format_class,
                        )
                    )
                StandardXML.Write_Row(
                    chunks[-1], fk, ff, fm[2], row_id=counter,
                )
            self.log_message(
                'wrote {0} rows to chunk {1}'.format(counter, len(chunks), ),
                category='debug',
            )
            self._end_chunk(chunks[-1])
        finally:
            self.log_message(
                'Message split into {0} chunks'.format(self._chunk_count, ),
                category='info',
            )

        zfile = zipfile.ZipFile(
            self.wfile, 'w',
            compression=zipfile.ZIP_DEFLATED,
        )
        for i in range(0, len(chunks)):
            sfile = NamedTemporaryFile(delete=False)
            shutil.copyfileobj(chunks[i], sfile)
            sfile.flush()
            BLOBManager.Close(chunks[i])
            zfile.write(
                sfile.name, arcname='StandardXML.chunk{0}.xml'.format(i, ),
            )
            sfile.close()

        zfile.close()

    def _start_chunk(self, table_name, format_name, format_class,):
        chunk = BLOBManager.ScratchFile()
        chunk.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        chunk.write(
            u'<ResultSet formatName=\"{1}\" '
            'className=\"{2}\" tableName=\"{0}\">'
            .format(table_name, format_name, format_class, )
        )
        self._chunk_count += 1
        return chunk

    def _end_chunk(self, chunk):
        chunk.write(u'</ResultSet>')
        # rewind and flush the current chunk
        chunk.seek(0)
        chunk.flush()

    def _set_anchor(self, keys, fields, metadata, ):
        for field_name in self._field_name:
            if field_name in keys:
                tmp = keys[field_name]
            elif field_name in fields:
                tmp = fields[field_name]
            else:
                tmp = None
        self._anchor_value = tmp

    def _new_chunk(self, keys, fields, metadata, ):
        for field_name in self._field_name:
            if field_name in keys:
                tmp = keys[field_name]
            elif field_name in fields:
                tmp = fields[field_name]
            else:
                tmp = None
            if not self._expression_callback(tmp):
                return False
        return True

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

    def _callback_change(self, value):
        result = (value == self._anchor_value)
        if not result:
            self.log_message(
                'key value changed from "{0}" to "{1}" @ row#{2}'
                .format(self._anchor_value, value, self._row_in, ),
                category='debug'
            )
        self._anchor_value = value
        return (not result)

    def parse_action_parameters(self):

        self._field_name = self._params.get('fieldName', None)
        if self._field_name is None:
            raise CoilsException('No field name specified for comparison.')
        self._field_name = [x.strip() for x in self._field_name.split(',')]

        cast_as = self._params.get('castAs', 'STRING').upper()

        self._compare_value = self._params.get('compareValue', None)

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
        elif expression == 'CHANGE':
            self._expression_callback = self._callback_change
            self._compare_value = 2020202020  # meaningless
        else:
            raise CoilsException(
                'Unknown comparision expression: "{0}", must be one '
                'of EQUALS, NOTEQUALS, IN, or REGEX.'
                .format(expression, )
            )

        self.log_message(
            'Split function is {0}'.format(self._expression_callback, ),
            category='debug',
        )
        if self._compare_value is None:
            raise CoilsException('No comparison value specified')
