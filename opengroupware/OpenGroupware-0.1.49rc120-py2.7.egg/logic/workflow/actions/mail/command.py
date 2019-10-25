#
# Copyright (c) 2018
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
import os
import zipfile
import tarfile
from email import message_from_file
from coils.core import SMTP
from coils.core.logic import ActionCommand


class MailAction(ActionCommand):

    def _get_message_from_input(self, mfile):
        return message_from_file(mfile)

    def _yield_input_handles_and_name(self):
        '''
        Yield tupes of handle & name from the input message
        '''

        # ZIP files must be this size or larger or else it will be
        # assumed to be empty.
        MIN_ZIPFILE_SIZE = 23

        def get_archive_size(rfile):
            rfile.seek(0, os.SEEK_END)  # go to end
            rfile_size = rfile.tell()  # get current offset
            rfile.seek(0, os.SEEK_SET)  # rewind
            return rfile_size

        rfile_size = get_archive_size(self.rfile)

        if self.input_mimetype in ('application/zip', ):

            """ZIP FILE"""

            self.log_message(
                'input message is a ZIP archive', category='debug'
            )

            if rfile_size < MIN_ZIPFILE_SIZE:
                """
                ZIP file is too small, it won't work, bail out.

                HACK: The Python zipfile module is buggy in relation to
                empty archives; this short-circuit hacks our way out of
                that mess. Some of this is fixed in Python 2.7.1; use that
                version or later if you can.
                """
                return

            # Process contents of ZipFile

            zfile = zipfile.ZipFile(self.rfile, 'r', )
            for zipinfo in zfile.infolist():
                zhandle = zfile.open(zipinfo, 'r')
                yield zhandle, zipinfo.filename
            zfile.close()
            return

        if self.input_mimetype in (
            'application/tar', 'application/x-tar', 'applicaton/x-gtar',
            'multipart/x-tar',
        ):
            tfile = tarfile.TarFile(
                fileobj=self.rfile,
            )
            for tinfo in tfile:
                if tinfo.isfile():
                    yield tfile.extractfile(tinfo), tinfo.name
            tfile.close()
            return

        """
        Default, return just the input message and its label
        NOTE: it is not mandatory that an action have an input_message, so
        we need to short-circuit around that condition.  However a message
        will always have [internally] an input and output streak [aka rfile
        and wfile - they might must be scratch files if there is no
        corresponding message].  As a messgae is not required to have a label
        this should not be a problem for conforming actions.
        """

        self.log_message(
            'assuming input messages is an RFC822 object', category='debug'
        )
        if self.input_message:
            yield self.rfile, self.input_message.label
        else:
            yield self.rfile, None
        return

    def _get_addresses_from_message(self, message):
        result = []
        if 'Cc' in message:
            result.extend(
                [x.strip() for x in message['Cc'].split(',')]
            )
        if 'To' in message:
            result.extend(
                [x.strip() for x in message['To'].split(',')]
            )
        return result

    def send_smtp_message(self, from_address, to_addresses, message, ):
        return SMTP.send(from_address, to_addresses, message, )
