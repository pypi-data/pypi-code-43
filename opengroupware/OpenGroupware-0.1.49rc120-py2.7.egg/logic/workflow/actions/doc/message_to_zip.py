#
# Copyright (c) 2015, 2016
#  Adam Tauno Williams <awilliam@whitemice.org>
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
import zipfile
from coils.core.logic import ActionCommand


class MessageToZIPFileAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "message-to-zipfile"
    __aliases__ = [
        'messageToZipFile', 'messageToZipFileAction',
        'messageToZip', 'messageToZipAction'
    ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'application/zip'

    def do_action(self):

        # Create the ZipFile object on the actions' write file handle
        zfile = zipfile.ZipFile(
            self.wfile, 'a', compression=zipfile.ZIP_DEFLATED,
        )
        zfile.write(self.rfile.name, arcname=self._filename, )
        self.log_message(
            'ZIP file created from message {0} labelled as "{1}"'
            .format(self.input_message.uuid, self.input_message.label, ),
            category='info',
        )
        zfile.close()

    def parse_action_parameters(self):

        self._filename = self.action_parameters.get(
            'filename', self.input_message.label
        )
        self._filename = self.process_label_substitutions(self._filename)
