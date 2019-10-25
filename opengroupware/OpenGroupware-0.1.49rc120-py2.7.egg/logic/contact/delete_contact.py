#
# Copyright (c) 2009, 2015
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
from coils.core import AccessForbiddenException
from coils.logic.address import DeleteCompany
from command import ContactCommand


class DeleteContact(DeleteCompany, ContactCommand):
    __domain__ = "contact"
    __operation__ = "delete"

    def __init__(self):
        DeleteCompany.__init__(self)

    def check_run_permissions(self):

        # Account objects cannot be deleted as accidental account deletion
        # can create a real mess.
        if self.obj.is_account:
            raise AccessForbiddenException(
                'Accounts cannot be deleted from the system; relieve the '
                'Contact object of account status, then delete.'
            )

        rights = self._ctx.access_manager.access_rights(self.obj, )
        if not set('dw').intersection(rights):
            raise AccessForbiddenException(
                'Cannot delete, insufficient access to {0}'.format(self.obj, )
            )

    def run(self):
        DeleteCompany.run(self)
