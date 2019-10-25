#
# Copyright (c) 2019
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
import os  # JUSTIFICATION: use of SEEK_SET
import smbc
import fnmatch
import zipfile
import shutil
from tempfile import NamedTemporaryFile
from coils.core.logic import ActionCommand


class SMBGetFilesAction(ActionCommand):
    """
    Retrieve files from an SMB/CIFS file server based on a file pattern
    into a ZIP file
    """
    __domain__ = "action"
    __operation__ = "smb-get-files"
    __aliases__ = [
        'smbGetFiles', 'smbGetFilesAction', 'smbGetFilesToZipAction',
        'sshGetFilesToZip',
    ]

    def __init__(self):
        ActionCommand.__init__(self)

    @property
    def result_mimetype(self):
        return u'application/zip'

    def authentication_callback(
        self, server, share, workgroup, username, password,
    ):
        return (
            self._domain_string, self._username_string, self._password_string,
        )

    def do_action(self):
        cifs = smbc.Context(auth_fn=self.authentication_callback)
        self.log_message('authentication context created', category='debug')
        self.log_message(
            'connecting to URL "{0}"'.format(self._share_uri, ),
            category='debug',
        )
        dent = cifs.opendir(self._share_uri)
        self.log_message('connected to resource', category='debug')
        dents = dent.getdents()
        filenames = [x.name for x in dents if x.smbc_type == 8]
        self.log_message(
            'discovered {0} filesystem objects'.format(len(filenames), ),
            category='debug',
        )
        matched_filenames = list()
        for filename in filenames:
            if fnmatch.fnmatch(filename, self._file_pattern):
                matched_filenames.append(filename)
            else:
                self.log_message(
                    'skipping file "{0}" due to file match pattern "{1}"'
                    .format(filename, self._file_pattern, ),
                    category='debug',
                )
        self.log_message(
            'retrieving {0} matching filesystem objects'
            .format(len(matched_filenames), ),
            category='debug',
        )

        # Create the ZipFile object on the actions' write file handle
        zfile = zipfile.ZipFile(
            self.wfile, 'a', compression=zipfile.ZIP_DEFLATED,
        )

        for filename in matched_filenames:

            full_file_path = '{0}/{1}'.format(self._share_uri, filename, )

            handle = cifs.open(full_file_path)
            """due to the dumbess that is the ZipFile module you have to give
            ZipFile's write method a filename rather than a simple hanlde;
            hence the use of NamedTemporary File."""
            sfile = NamedTemporaryFile(delete=False)
            shutil.copyfileobj(handle, sfile)
            handle.close()
            sfile.seek(0, os.SEEK_SET)
            zfile.write(sfile.name, arcname=filename, )
            self.log_message(
                '{0} octets retrieved from file "{1}"'
                .format(sfile.tell(), full_file_path, ),
                category='info',
            )
            sfile.close()

        zfile.close()  # close the ZIP file
        self.wfile.flush()

        # TODO: this output message should be saved somehow even if the
        # subsequent deletion fails

        if self._delete_after:
            for filename in matched_filenames:
                full_file_path = '{0}/{1}'.format(self._share_uri, filename, )
                self.log_message(
                    'attempting to delete "{0}"'.format(full_file_path, ),
                    category='info',
                )
                cifs.unlink(full_file_path)

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
        self._share_uri = self.process_label_substitutions(
            self.action_parameters.get('shareuri')
        )
        self._file_pattern = self.process_label_substitutions(
            self.action_parameters.get('filepattern', '*')
        )

        if self.action_parameters.get('deleteAfter', 'NO').upper() == 'YES':
            self._delete_after = True
        else:
            self._delete_after = False

    def do_epilogue(self):
        pass
