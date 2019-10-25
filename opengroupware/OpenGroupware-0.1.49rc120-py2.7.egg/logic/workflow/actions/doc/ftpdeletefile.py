#
# Copyright (c)  2013, 2014
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
from ftplib import FTP
from ftplib import error_perm, error_reply
from coils.core.logic import ActionCommand


class FTPDeleteFileAction(ActionCommand):
    """
    Delete a file from an FTP server
    """
    __domain__ = "action"
    __operation__ = "ftp-delete-file"
    __aliases__ = ['ftpDeleteFile', 'ftpDeleteFileAction', ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return 'text/plain'

    def do_action(self):

        ftp = FTP(self._hostname)
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
            self.log_message(
                message=(
                    'Changed current working directory to "{0}".'
                    .format(ftp.pwd(), )
                ),
                category='debug',
            )

        self._filename = self._filename.strip()
        if len(self._filename) == 0:
            raise CoilsException(
                'ftpDeleteFileAction will not attempt to delete a '
                'zero-length filename.'
            )

        try:
            response = ftp.delete(self._filename, )
            self.wfile.write(response)
        except error_perm as exc:
            if not self._ignore_fail:
                raise exc
            self.log_message(
                message=(
                    'FTP delete of "{0}" failed due to permissions'
                    .format(self._filename, )
                ),
                category='debug',
            )
        except error_reply as exc:
            if not self._ignore_fail:
                raise exc
            self.log_message(
                message=(
                    'FTP delete of "{0}" failed due to unspecified reasons'
                    .format(self._filename, )
                ),
                category='debug',
            )
        else:
            self.log_message(
                message=(
                    'File "{0}" deleted from FTP service.'.format(self._filename, )
                ),
                category='debug',
            )
        finally:
            ftp.quit()


    def parse_action_parameters(self):

        self._hostname = self.process_label_substitutions(
            self.action_parameters.get('server')
        )
        self._filename = self.process_label_substitutions(
            self.action_parameters.get('filename')
        )

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

        passive = self.process_label_substitutions(
            self.action_parameters.get('passive', 'YES')
        )
        if not passive.upper() == 'NO':
            self._passive = True
        else:
            self._passive = False

        ignore_fail = self.process_label_substitutions(
            self.action_parameters.get('ignore_fail', 'NO')
        )
        self._ignore_fail = False if not ignore_fail.upper() == 'YES' else True
