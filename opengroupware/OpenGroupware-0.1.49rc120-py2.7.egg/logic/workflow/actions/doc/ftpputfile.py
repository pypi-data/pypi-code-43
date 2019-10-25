#
# Copyright (c) 2012, 2013, 2016, 2019
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
#
import os
import socket
import zipfile
import tarfile
import time
from ftplib import FTP
from coils.core.logic import ActionCommand


ARCHIVE_ZIP_TYPES = ('application/zip', )


ARCHIVE_TAR_TYPES = ('application/tar', 'application/x-tar',
                     'applicaton/x-gtar', 'multipart/x-tar', )


class FTPPutFileAction(ActionCommand):
    __domain__ = "action"
    __operation__ = "ftp-put-file"
    __aliases__ = ['ftpPutFile', 'ftpPutFileAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

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

        if (
            (self.input_mimetype in ARCHIVE_ZIP_TYPES) and
            self._unpack_archives
        ):
            """ZIP FILE"""
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

        if (
            (self.input_mimetype in ARCHIVE_TAR_TYPES) and
            self._unpack_archives
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
        if self.input_message:
            yield self.rfile, self._filename
        else:
            yield self.rfile, None
        return

    def authentication_callback(
        self,
        server,
        share,
        workgroup,
        username,
        password,
    ):
        return (
            self._domain_string,
            self._username_string,
            self._password_string,
        )

    def do_action(self):

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

        ftp.set_pasv(self._passive)

        if not self._username:
            ftp.login()
        else:
            ftp.login(self._username, self._password)

        if self._directory:
            ftp.cwd(self._directory)

        for r_handle, r_name, in self._yield_input_handles_and_name():
            ftp.storbinary('STOR {0}'.format(r_name), r_handle)
            self.log_message(
                'wrote file "{0}"'.format(r_name, ),
                category='info',
            )
            r_handle.close()

        ftp.quit()

    def parse_action_parameters(self):

        self._hostname = self.process_label_substitutions(
            self.action_parameters.get('server')
        )
        self._filename = self.process_label_substitutions(
            self.action_parameters.get('filename', self.input_message.label, )
        )

        self._passive = self.process_label_substitutions(
            self.action_parameters.get('passive', 'YES')
        )
        if not self._passive.upper() == 'NO':
            self._passive = True
        else:
            self._passive = False

        self._username = self.action_parameters.get('username', None)
        if self._username:
            self._username = self.process_label_substitutions(self._username)
            self._password = self.action_parameters.get(
                'password',
                '$__EMAIL__;',
            )
            self._password = self.process_label_substitutions(self._password)

        self._directory = self.action_parameters.get('directory', None)
        if self._directory:
            self._directory = self.process_label_substitutions(self._directory)

        self._unpack_archives = (
            True if self.action_parameters.get(
                'unpackArchives', 'NO'
            ).upper() == 'YES' else False
        )

    def do_epilogue(self):
        pass
