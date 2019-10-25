#
# Copyright (c) 2014, 2016
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
import re
import socket
import time
import zipfile
from ftplib import FTP
from coils.core import BLOBManager
from coils.core.logic import ActionCommand


EMPTY_ZIP_FILE = (
    'PK\x05\x06\x00\x00\x00\x00\x00\x00\x00\x00'
    '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
)


class FTPGetFilesAction(ActionCommand):
    """
    Retrieve a file from an FTP server
    """
    __domain__ = "action"
    __operation__ = "ftp-get-files"
    __aliases__ = ['ftpGetFiles', 'ftpGetFilesAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'application/zip'

    def _write_block_to_sfile(self, data):
        self._sfile.write(data)
        self._offset += len(data)

    def do_action(self):

        included_documents = list()

        self._offset = 0

        """
        Initial attempt to resolve host name; this helps deal with very
        slow or pausey DNS servers.
        """
        try:
            socket.getaddrinfo(self._hostname, None, 0)
        except socket.gaierror as exc:
            if exc.errno == -2:
                self.log_message(
                    (
                        'Initial attempt to resolving hostname "{0}" failed; '
                        'action will sleep briefly then attempt to connect'
                        .format(self._hostname, )
                    ),
                    category='error',
                )
                time.sleep(0.5)
            else:
                raise exc

        try:
            ftp = FTP(self._hostname)
        except socket.gaierror as exc:
            if exc.errno == -2:
                self.log_message(
                    (
                        'Resolving hostname "{0}" failed.'
                        .format(self._hostname, )
                    ),
                    category='error',
                )
                raise exc
            else:
                raise exc

        self.log_message(
            message=(
                'Connected to FTP service "{0}"'.format(self._hostname, )
            ),
            category='debug',
        )

        ftp.set_pasv(self._passive)

        if not self._username:
            ftp.login()
        else:
            ftp.login(self._username, self._password)
        self.log_message(
            message='Authenticated to FTP service',
            category='debug',
        )

        if self._directory:
            ftp.cwd(self._directory)

        # Create a new ZIP file
        zfile = zipfile.ZipFile(
            self.wfile, 'a', compression=zipfile.ZIP_DEFLATED,
        )

        self._sfile = None  # reference the currently used scratch file
        scratches = list()  # maintain a list of the opened scratch files

        for filename in ftp.nlst():
            if self._expression is None or self._expression.match(filename):
                self._offset = 0  # Reset file read offset counter
                self._sfile = BLOBManager.ScratchFile(require_named_file=True)
                scratches.append(self._sfile)

                ftp.retrbinary(
                    'RETR {0}'.format(filename, ),
                    callback=self._write_block_to_sfile,
                )

                self.log_message(
                    message=(
                        'File "{0}" retrieved ({1} octets)'
                        .format(filename, self._offset, )
                    ),
                    category='debug',
                )

                included_documents.append(filename)

                # Append the retrieved file into the ZIP file
                self._sfile.flush()
                self._sfile.seek(0)  # Rewind
                zfile.write(
                    self._sfile.name,
                    arcname=filename,
                )  # Add the scratch file to the Zip file
                self.log_message(
                    message=(
                        'File "{0}" appended to ZIP archive'
                        .format(filename, )
                    ),
                    category='debug',
                )

                self._sfile = None
            else:
                self.log_message(
                    message=(
                        'File "{0}" skipped.'.format(filename, )
                    ),
                    category='debug',
                )

        ftp.quit()

        zfile.close()

        self.log_message(
            message='ZIP archive closed',
            category='debug',
        )

        self.wfile.flush()

        if self.wfile.tell() == 0:
            """
            Work around for bad zipfile modules that create zero-sized empty
            files; as of Python 2.7.1 this would not be a problem but prior
            versions fail to write the header when nothing has been appended
            to the file - yes, this bug exists even if you write a comment into
            the metadata of the zip file.
            """
            self.log_message(
                message=(
                    'Writing ZIP header for empty archive; Python is  < 2.7.1?'
                ),
                category='debug',
            )
            self.wfile.write(EMPTY_ZIP_FILE)

        for sfile in scratches:
            #  Close all the open scratch files
            BLOBManager.Close(sfile)
        scratches = None

        self.log_message(
            message=(
                '{0} files retrieved from FTP server.'
                .format(len(included_documents), )
            ),
            category='debug',
        )

    def parse_action_parameters(self):

        # FTP Server name: "server"
        self._hostname = self.process_label_substitutions(
            self.action_parameters.get('server')
        )

        # Switch to passive mode? "passive"
        passive = self.process_label_substitutions(
            self.action_parameters.get('passive', 'YES')
        )
        self._passive = True if not passive.upper() == 'NO' else False

        # Credentials, if no password is provided we default to the current
        # context's e-mail address - "username" & "password"
        self._username = self.action_parameters.get('username', None)
        if self._username:
            self._username = self.process_label_substitutions(self._username)
            self._password = self.action_parameters.get(
                'password',
                '$__EMAIL__;',
            )
            self._password = self.process_label_substitutions(self._password, )

        # Directory to change to - "directory"
        self._directory = self.action_parameters.get('directory', None)
        if self._directory:
            self._directory = self.process_label_substitutions(
                self._directory,
            )

        # Compile regular expression if provided - "expression"
        self._expression = self.action_parameters.get('expression', None)
        if self._expression:
            self._expression = re.compile(
                self.process_label_substitutions(
                    self._expression,
                )
            )

    def do_epilogue(self):
        pass
