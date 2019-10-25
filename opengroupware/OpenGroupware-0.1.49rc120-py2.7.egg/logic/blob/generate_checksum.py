#
# Copyright (c) 2016
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
from coils.core import \
    CoilsException, \
    Command, \
    BLOBManager
from command import BLOBCommand


class GenerateDocumentChecksum(Command, BLOBCommand):
    __domain__ = "document"
    __operation__ = "generate-checksum"

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.obj = params.get('document', None)
        self._version = int(params.get('version', 1))

    def run(self, **params):
        # Failure to marshall a BLOBManager will raise an exception on its own
        checksum = None
        manager = self.get_manager(self.obj)
        if manager:
            rfile = self.get_handle(
                manager, 'rb', self.obj,
                version=self._version,
                encoding='binary',
            )
            wfile = BLOBManager.ScratchFile()
            checksum, size, = self.write(rfile, wfile)
            self.set_result(checksum)
        else:
            raise CoilsException(
                'Unable to marshall content manager for '
                'OGo#{0} [Document] version #{1}'
                .format(self.obj.object_id, self._version, )
            )
