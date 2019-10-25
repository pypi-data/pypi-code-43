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
import shutil
import zipfile
from tempfile import NamedTemporaryFile
from coils.core import StandardXML, CoilsException
from coils.foundation import BLOBManager
from coils.core.logic import ActionCommand


class GroupByAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "group-by"
    __aliases__ = ['groupBy', 'groupByAction', ]

    def __init__(self):
        ActionCommand.__init__(self)
        self._chunk_index = dict()
        self._current_chunk = None

    @property
    def result_mimetype(self):
        return u'application/zip'

    def do_action(self):
        self._row_in = 0
        skipped_rows = 0
        self._table_name, self._format_name, self._format_class = \
            StandardXML.Read_ResultSet_Metadata(self.rfile)
        try:
            for fk, ff, fm, in StandardXML.Read_Rows(
                self.rfile, with_metadata=True
            ):
                self._row_in += 1
                if self._get_chunk(fk, ff, fm):
                    StandardXML.Write_Row(
                        self.current_chunk, fk, ff, fm[2], row_id=self._row_in,
                    )
                else:
                    skipped_rows += 1
                    self.log_message(
                        'discarding row {0}, no chunk available'
                        .format(self._row_in, ),
                        category='debug',
                    )
        finally:
            self.log_message(
                'Message split into {0} chunks, total of {1} rows.'
                .format(self.chunk_count, self._row_in,),
                category='info',
            )
            self.log_message(
                '{0} rows skipped due to noChunk condition'
                .format(skipped_rows, ),
                category='info',
            )

        for chunk in self.chunk_index.values():
            self._end_chunk(chunk)

        zfile = zipfile.ZipFile(
            self.wfile, 'w',
            compression=zipfile.ZIP_DEFLATED,
        )
        for key, chunk in self._chunk_index.items():
            sfile = NamedTemporaryFile(delete=False)
            shutil.copyfileobj(chunk, sfile)
            sfile.flush()
            BLOBManager.Close(chunk)
            zfile.write(
                sfile.name, arcname='StandardXML.chunk{0}.xml'.format(key, ),
            )
            sfile.close()

        zfile.close()

    @property
    def chunk_index(self):
        return self._chunk_index

    @property
    def chunk_count(self):
        return len(self._chunk_index)

    @property
    def current_chunk(self):
        return self._current_chunk

    def _start_chunk(self, gv):
        chunk = BLOBManager.ScratchFile()
        chunk.write(u'<?xml version="1.0" encoding="UTF-8"?>')
        chunk.write(
            u'<ResultSet formatName=\"{1}\" '
            'className=\"{2}\" tableName=\"{0}\">'
            .format(
                self._table_name,
                self._format_name,
                self._format_class,
            )
        )
        self.log_message(
            'new chunk "{0}" created at row {1}'.format(gv, self._row_in, ),
            category='debug',
        )
        self._chunk_index[gv] = chunk
        return chunk

    def _end_chunk(self, chunk):
        chunk.write(u'</ResultSet>')
        # rewind and flush the current chunk
        chunk.flush()
        chunk.seek(0)

    def _get_chunk(self, keys, fields, metadata, ):
        gv = self._get_groupby_value(keys, fields, )
        if self._current_chunk is None:
            self.log_message(
                'initial chunk is "{0}"'.format(gv, self._row_in, ),
                category='debug'
            )
            self._start_chunk(gv)
        if gv is not None:
            """
            do not change chunks if the groupByValue is None
            the record may have been filtered out by the key value
            filter
            """
            if not (gv in self._chunk_index):
                self._start_chunk(gv)
            self.log_message(
                'selecting chunk "{0}" at row {1}'.format(gv, self._row_in, ),
                category='debug'
            )
            self._current_chunk = self._chunk_index.get(gv, None)
        if (self._current_chunk is None):
            return False
        return True

    def _get_groupby_value(self, keys, fields, ):
        if self._key_field:
            kv = keys.get(self._key_field, fields.get(self._key_field, None))
            if not (kv == self._key_value):
                return None
        gv = keys.get(
            self._group_key, fields.get(self._group_key, None)
        )
        if gv is None:
            raise CoilsException(
                'GroupBy value "{0}" is NULL or not found'
                .format(self.self._group_key, )
            )
        if gv is not None:
            if self._group_cast == 'INTEGER':
                gv = int(gv)
            elif self._group_cast == 'FLOAT':
                gv = float(gv)
            else:
                gv = str(gv)
        return gv

    def parse_action_parameters(self):

        self._key_field = self._params.get('keyField', None)
        if self._key_field:
            key_value = self._params.get('keyValue', None)
            key_castas = self._params.get('keyCastAs', 'STRING').upper()
            if key_castas == 'INTEGER':
                self._key_value = int(key_value.strip())
            elif key_castas == 'FLOAT':
                self._key_value = float(key_value.strip())
            else:
                self._key_value = str(key_value.strip())

        self._group_key = self._params.get('groupKey', None)
        if self._group_key is None:
            raise CoilsException('No groupKey specified for groupByAction')
        self._group_cast = self._params.get(
            'groupValueCastAs', 'STRING'
        ).upper()
