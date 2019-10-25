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
from string import atoi
from coils.core import CoilsException
from coils.core.logic import ActionCommand
from command import SSHAction


class SSHCreateFolderAction(ActionCommand, SSHAction):
    __domain__ = "action"
    __operation__ = "ssh-create-directory"
    __aliases__ = [
        'sshCreateDirectory', 'sshCreateDirectoryAction, sshMKDIR', ]
    mode = None

    def __init__(self):
        ActionCommand.__init__(self)

    def parse_action_parameters(self):
        ActionCommand.parse_action_parameters(self)

        SSHAction.parse_action_parameters(self)

        self._folder_name = self.action_parameters.get('folderPath', None)
        self._folder_name = self.process_label_substitutions(self._folder_name)

        self._filemode = self.action_parameters.get('fileMode', '770')
        if self._filemode:
            self._filemode = self.process_label_substitutions(self._filemode)
            try:
                self._filemode = atoi(self._filemode, 8)
            except:
                raise CoilsException(
                    'Specified fileMode "{0}" is not a valid octal value'
                    .format(self._filemode, )
                )

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

        # TODO: support recursive path creation
        ftp = transport.open_sftp_client()
        ftp.mkdir(self._folder_name, mode=self._filemode)
        ftp.close()
        self.close_transport(transport=transport)

        self.wfile.write(self._folder_name)
