#
# Copyright (c) 2012, 2013, 2017, 2018
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
from string import atoi
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from command import SSHAction

ARCHIVE_MIME_TYPES = (
    'application/tar', 'application/x-tar', 'applicaton/x-gtar',
    'multipart/x-tar', 'application/zip',
)


class SSHPutFileAction(ActionCommand, SSHAction):
    __domain__ = "action"
    __operation__ = "ssh-put-file"
    __aliases__ = ['sshPutFileAction', 'sshPutFile', ]
    mode = None

    def __init__(self):
        ActionCommand.__init__(self)

    def parse_action_parameters(self):
        ActionCommand.parse_action_parameters(self)

        SSHAction.parse_action_parameters(self)

        self._unpack_archives = (
            True if self.action_parameters.get(
                'unpackArchives', 'NO'
            ).upper() == 'YES' else False
        )

        self._filename = self.action_parameters.get('filePath', None)
        if not self._filename:
            raise CoilsException(
                'No filename provided for sshPutFileAction action'
            )
        self._filename = self.process_label_substitutions(self._filename)

        self._filemode = self.action_parameters.get('fileMode', None)
        if self._filemode:
            self._filemode = self.process_label_substitutions(self._filemode)
            try:
                self._filemode = atoi(self._filemode, 8)
            except:
                raise CoilsException(
                    'Specified fileMode "{0}" is not a valid octal value'
                    .format(self._filemode, )
                )

        self._do_overwrite = (
            True if self.action_parameters.get(
                'allowOverwrite', 'YES'
            ).upper() == 'YES' else False
        )

    def _put_file(self, transport, handle, filename):
        wfile, transport, = self.put_file(
            transport=transport,
            path=filename,
            rfile=handle,
            close_after=False,
        )
        try:
            if self._filemode:
                wfile.chmod(self._filemode)
        except Exception as exc:
            raise CoilsException(
                'Failed to set filemode to specified value of "{0}" on "{1}"'
                .format(self._filemode, filename, ),
                inner_exception=exc,
            )
        finally:
            wfile.close()

    def do_action(self):
        self.initialize_client()
        key_path, key_handle, = self.resolve_private_key()
        private_key = self.initialize_private_key(
            path=key_path,
            handle=key_handle,
            password=self._secret,
            key_type=self._key_type,
        )
        transport = self.initialize_transport(self._hostname, self._hostport)
        if not self.authenticate(
            transport=transport,
            username=self._username,
            private_key=private_key,
        ):
            raise CoilsException(
                'Unable to complete SSH authentication'
            )
        if (
            (self.input_mimetype in ARCHIVE_MIME_TYPES) and
            self._unpack_archives
        ):
            self._send_archive(transport)
        else:
            # not an archive
            if not self._do_overwrite:
                # do not overwrite is ENABLED
                info = self.get_fileinfo(transport, self._filename)
                if info:
                    if info.size > 0:
                        raise CoilsException(
                            'Action will overwrite existing file "{0}" which '
                            'is not zero-sized.'.format(self._filename, )
                        )
            # get the file
            self._put_file(transport, self.rfile, self._filename)
        self.close_transport(transport=transport)

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
        if self.input_message:
            yield self.rfile, self.input_message.label
        else:
            yield self.rfile, None
        return

    def _send_archive(self, transport):
        for handle, filename, in self._yield_input_handles_and_name():
            self._put_file(
                transport,
                handle,
                os.path.join(self._filename, filename),
            )
            self.log_message(
                'put file "{0}" from archive'.format(filename, ),
                category='info',
            )
