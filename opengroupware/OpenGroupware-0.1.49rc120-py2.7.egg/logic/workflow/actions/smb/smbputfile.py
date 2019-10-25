#
# Copyright (c) 2012, 2014, 2018, 2019
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
import os
import smbc
from shutil import copyfileobj
from coils.core import CoilsException
from coils.core.logic import ActionCommand


class SMBPutFileAction(ActionCommand):
    """
    Put the input message as a file to an SMB/CIFS file server
    """
    __domain__ = "action"
    __operation__ = "smb-put-file"
    __aliases__ = ['smbPutFile', 'smbPutFileAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def authentication_callback(
        self, server, share, workgroup, username, password,
    ):
        return (
            self._domain_string, self._username_string, self._password_string,
        )

    def do_action(self):
        self.log_message(
            'Writing message to {0} as user {1}\\{2}'
            .format(
                self._target_unc,
                self._domain_string,
                self._username_string,
            ),
            category='debug',
        )
        cifs = smbc.Context(auth_fn=self.authentication_callback)

        if not(self._do_overwrite):
            try:
                cifs.stat(self._target_unc)
            except smbc.NoEntryError:
                # cool cool, no such file exists
                pass
            else:
                raise CoilsException(
                    'Target Object "{0}" already exists.'
                    .format(self._target_unc, )
                )

        try:
            handle = cifs.open(
                self._target_unc, os.O_CREAT | os.O_WRONLY | os.O_TRUNC,
            )
        except ValueError as exc:
            if exc.args[1] == 'Invalid argument':
                self.log_message(
                    'Invalid argument: target="{0}" @ {1}'.format(
                        self._target_unc, cifs,
                    )
                )
            raise exc
        copyfileobj(self._rfile, handle)
        handle.close()

    def parse_action_parameters(self):
        self._domain_string = self.process_label_substitutions(
            self.action_parameters.get('domain')
        )
        self._password_string = self.process_label_substitutions(
            self.action_parameters.get('password')
        )
        self._username_string = self.process_label_substitutions(
            self.action_parameters.get('username')
        )
        self._target_unc = self.process_label_substitutions(
            self.action_parameters.get('target')
        )

        self._do_overwrite = (
            True if self.action_parameters.get(
                'allowOverwrite', 'YES'
            ).upper() == 'YES' else False
        )

    def do_epilogue(self):
        pass
