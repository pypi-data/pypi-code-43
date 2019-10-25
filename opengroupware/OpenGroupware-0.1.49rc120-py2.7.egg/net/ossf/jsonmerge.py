#
# Copyright (c) 2017
#   Adam Tauno Williams <awilliam@whitemice.org>
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
import json
from coils.core import \
    NotImplementedException, \
    BLOBManager, \
    CoilsException, \
    NetworkContext
from filter import OpenGroupwareServerSideFilter


class JSONMergeOSSFilter(OpenGroupwareServerSideFilter):

    @property
    def handle(self):

        if (self._mimetype != 'application/json'):
            raise Exception(
                'Input type for JSONDecoder is not mimetype application/json'
            )
        if not (hasattr(self, '_documentid')):
            raise NotImplementedException('No documentId specified for merge.')

        if self._ctx is None:
            self._ctx = NetworkContext()

        document = self._ctx.run_command(
            'document::get', id=self._documentid,
        )
        if not document:
            raise CoilsException(
                'Unable to marshall document OGo#{0}'
                .format(self._documentid, )
            )
        mimetype = self._ctx.type_manager.get_mimetype(document)
        if mimetype not in ('application/json'):
            raise CoilsException(
                'Merge document is not an application/json stream'
            )
        handle = self._ctx.run_command(
            'document::get-handle', document=document,
        )

        self._merge_document_handle = None
        if not handle:
            raise CoilsException(
                'Unable to marshall stream for document OGo#{0}'
                .format(self._documentid, )
            )
        else:
            self._merge_document_handle = handle

        source_data = json.load(self.rfile)
        if not isinstance(source_data, dict):
            self.handle.seek(0)
            return self.handle

        merge_data = json.load(self._merge_document_handle)
        result = dict()
        for key, item in source_data.items():
            result[key] = item
            if not isinstance(item, dict):
                continue
            if key in merge_data:
                for key_, item_ in merge_data[key].items():
                    result[key][key_] = item_

        scratch = BLOBManager.ScratchFile()
        json.dump(result, scratch)
        scratch.seek(0)
        source_data = merge_data = result = None
        return scratch

    @property
    def mimetype(self):
        return 'application/json'
