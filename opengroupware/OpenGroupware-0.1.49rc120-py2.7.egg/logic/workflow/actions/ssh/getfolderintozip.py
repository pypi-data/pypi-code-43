#
# Copyright (c) 2017
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
# SOFTWARE
#
import zipfile
import shutil
from tempfile import NamedTemporaryFile
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from command import SSHAction


class SSHGetFolderIntoZipFileAction(ActionCommand, SSHAction):
    __domain__ = "action"
    __operation__ = "ssh-get-folder-to-zipfile"
    __aliases__ = ['sshGetFolderToZipAction', 'sshGetFolderToZip', ]
    mode = None

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'application/zip'

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
        gathered_files = list()
        for filepath in ftp.listdir(self._folderpath):
            full_path = '{0}/{1}'.format(self._folderpath, filepath, )
            try:
                self.log_message(
                    'retrieving file "{0}"'.format(full_path, ),
                    category='debug',
                )
                rfile = ftp.open(full_path)
            except IOError as e:
                if e.errno == 2 and self._skip_missing:
                    self.log_message(
                        'skipping file "{0}" - missing'.format(full_path, ),
                        category='info',
                    )
                    pass
            else:
                sfile = NamedTemporaryFile(delete=False)
                shutil.copyfileobj(rfile, sfile)
                sfile.flush()
                rfile.close()
                zfile.write(sfile.name, arcname=filepath, )
                self.log_message(
                    'file "{0}" retrieved as {1} octets'
                    .format(full_path, sfile.tell(), ),
                    category='info',
                )
                sfile.close()
                gathered_files.append(full_path)
        zfile.close()

        self._ctx.flush()

        if self._deleted_files and gathered_files:
            self.log_message('deleting retrieved files', category='info', )
            for fullpath in gathered_files:
                self.log_message(
                    'deleting "{0}"'.format(fullpath, ),
                    category='info',
                )
                ftp.remove(fullpath)  # delete file

        self.log_message('closing transport', category='debug', )
        self.close_transport(transport=transport)

    def parse_action_parameters(self):
        ActionCommand.parse_action_parameters(self)

        SSHAction.parse_action_parameters(self)

        self._folderpath = self.action_parameters.get('folderPath', None)
        self._folderpath = self.process_label_substitutions(self._folderpath)

        if self.action_parameters.get('deleteFiles', 'NO').upper() == 'YES':
            self._deleted_files = True
        else:
            self._deleted_files = False
