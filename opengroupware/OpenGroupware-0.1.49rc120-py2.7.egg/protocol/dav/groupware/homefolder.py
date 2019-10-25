# Copyright (c) 2016, 2017
# Adam Tauno Williams <awilliam@whitemice.org>
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
# THE SOFTWARE.
#
from documentsfolder import DocumentsFolder
from coils.core import NoSuchPathException, CoilsException


class HomeFolder(DocumentsFolder):
    def __init__(self, parent, name, **params):
        DocumentsFolder.__init__(self, parent, name, **params)
        self._home_folder = None
        self._home_project = None

    def __repr__(self):
        return (
            '<HomeFolder path="{0}" contextId="{1}" login="{2}"/>'
            .format(
                self.get_path(),
                self.context.account_id,
                self.context.login,
            )
        )

    @property
    def entity(self):
        if self._home_folder is not None:
            return self._home_folder

        self._home_project = self.context.run_command(
            'project::get-home-project'
        )
        if not self._home_project:
            self._home_project = self.context.run_command(
                'project::new-home-project'
            )
            if self._home_project:
                self.context.commit()  # is this OK?
        if self._home_project:
            self._home_folder = self.context.run_command(
                'project::get-root-folder',
                project=self._home_project,
            )
            if self._home_folder:
                return self._home_folder

            raise CoilsException(
                'Unable to marshall root folder of home project, '
                'OGo#{0}'.format(self._home_project.object_id, )
            )

        raise NoSuchPathException(
            'No home project found for current identity OGo#{0}'
            .format(self.context.account_id, )
        )

    def _load_self(self):
        if self.context.account_id < 10001:
            return True
        return DocumentsFolder._load_self(self)
