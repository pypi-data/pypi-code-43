#
# Copyright (c) 2012, 2013, 2017
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
import zipfile
import shutil
import traceback
from os.path import basename
from tempfile import NamedTemporaryFile
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from command import SSHAction


class SSHGetFilesIntoZipFileAction(ActionCommand, SSHAction):
    __domain__ = "action"
    __operation__ = "ssh-gets-files-to-zipfile"
    __aliases__ = ['sshGetFilesToZipAction', 'sshGetFilesToZip', ]
    mode = None

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'application/zip'

    def parse_action_parameters(self):
        ActionCommand.parse_action_parameters(self)

        SSHAction.parse_action_parameters(self)

        if self.action_parameters.get('skipMissing', 'YES').upper() == 'YES':
            self._skip_missing = True
        else:
            self._skip_missing = False

        if self.action_parameters.get('stripPath', 'YES').upper() == 'YES':
            self._strip_path = True
        else:
            self._strip_path = False

        if self.action_parameters.get('deleteAfter', 'NO').upper() == 'YES':
            self._delete_after = True
        else:
            self._delete_after = False

        self._filepaths = self.action_parameters.get('filePaths', None)
        self._filepaths = self.process_label_substitutions(self._filepaths)
        self._filepaths = [x.strip() for x in self._filepaths.split(',')]

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
            raise CoilsException('Unable to complete SSH authentication')
        ftp = transport.open_sftp_client()
        # get many files
        zfile = zipfile.ZipFile(
            self.wfile, 'w',
            compression=zipfile.ZIP_DEFLATED,
        )
        # wildcard support! 2017-04-21
        file_list = list()
        for filepath in self._filepaths:
            tmp = self.match_files(ftp, filepath)
            if not tmp:
                # no files match path/pattern
                self.log_message(
                    'file path "{0}" matched no files'.format(filepath, ),
                    category='info',
                )
                # missing files not permitted?
                if not self._skip_missing:
                    raise CoilsException(
                        'No files match filepath "{0}"'
                        .format(filepath, )
                    )
            else:
                self.log_message(
                    'file path "{0}" matched: {1}'
                    .format(filepath, ','.join(tmp), ),
                    category='info',
                )
                file_list.extend(tmp)
        self.log_message(
            '{0} filepaths matched {1} files'
            .format(len(self._filepaths), len(file_list), ),
            category='debug',
        )
        # retrieve file(s)
        for filepath in file_list:
            try:
                rfile = ftp.open(filepath)
            except IOError as exc:
                rfile = None
                if exc.errno == 2 and self._skip_missing:
                    self.log_message(
                        'file "{0}" is missing!'.format(filepath, ),
                        category='warn',
                    )
                else:
                    raise exc
            if not rfile:
                continue
            sfile = NamedTemporaryFile(delete=False)
            shutil.copyfileobj(rfile, sfile)
            sfile.flush()
            rfile.close()
            if self._strip_path:
                zfile.write(sfile.name, arcname=basename(filepath), )
            else:
                zfile.write(sfile.name, arcname=filepath, )
            self.log_message(
                '{0} octets retrieved from file "{1}"'
                .format(sfile.tell(), filepath, ),
                category='debug',
            )
            sfile.close()
        zfile.close()

        # flush, so we know we are near success before we delete stuff
        self._ctx.flush()

        if self._delete_after:
            for filepath in file_list:
                self.log_message(
                    'deleting "{0}"'.format(filepath, ), category='debug',
                )
                try:
                    ftp.remove(filepath)
                except IOError:
                    self.log_message(
                        'exception deleting "{0}"\n{1}'
                        .format(filepath, traceback.format_exc(), ),
                        category='debug',
                    )
                else:
                    self.log_message(
                        'deleted "{0}"'.format(filepath, ),
                        category='info',
                    )

        self.close_transport(transport=transport)

        file_list = None
