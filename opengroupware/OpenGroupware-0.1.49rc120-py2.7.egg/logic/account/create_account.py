#
# Copyright (c) 2009, 2012, 2015, 2018
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
#
import shutil
from coils.foundation import ServerDefaultsManager
from coils.core import \
    BLOBManager, \
    AccessForbiddenException, \
    OGO_ROLE_SYSTEM_ADMIN, \
    CoilsException, \
    Contact, \
    Command


class CreateAccount(Command):
    __domain__ = "account"
    __operation__ = "new"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

        self.login = params.get('login', None)
        self.password = params.get('password', None)
        self.template_id = params.get('template_id', 9999, )
        self.obj = params.get('contact', None)

        if not self.template_id:
            self.template_id = 9999  # the default template account
        else:
            try:
                self.template_id = int(self.template_id)
            except:
                raise CoilsException(
                    'template_id for account must be an integer, '
                    'provided value "{0}" is of type {1}'
                    .format(self.template_id, type(self.template_id, ), )
                )

        if not self.login:
            raise CoilsException('No login value specified for new account')

        if not self.obj:
            raise CoilsException('No "contact" provided to account::new')

        if not isinstance(self.obj, Contact):
            raise CoilsException(
                'Contact provided to account::new is not a '
                'contact entity, type is {0}'
                .format(type(self.obj), )
            )

    def check_run_permissions(self):
        if self._ctx.has_role(OGO_ROLE_SYSTEM_ADMIN):
            return
        raise AccessForbiddenException(
            'Context lacks administrative role; cannot create accounts.'
        )

    def run(self):
        # TODO: Verify that the template_id provided identifies a real entity?
        if not self.obj.is_account:
            self.obj.is_account = 1
            self.obj.template_user_id = self.template_id
            self.obj.login = self.login
            if self.password:
                self._ctx.run_command(
                    'account::set-password',
                    login=self.obj.login,
                    password=self.password,
                )
        else:
            raise CoilsException(
                'OGo#{0} [Contact] is already an account'
                .format(self.obj.object_id, )
            )
        """
        if we have violated database constraints we want to know now before
        we potentially copy the template user's preferences to the new account
        """
        self._ctx.flush()

        """
        if there is a template account we want to copy those preferences to
        the new accounts' defaults file
        """
        if self.obj.template_user_id:
            rfile = BLOBManager.Open(
                'documents/{0}.defaults'.format(self.obj.template_user_id, ),
                'rb',
                encoding=ServerDefaultsManager.__encoding__,
                create=False,
            )
            if rfile:
                wfile = BLOBManager.Open(
                    'documents/{0}.defaults'.format(self.obj.object_id, ),
                    'wb',
                    encoding=ServerDefaultsManager.__encoding__,
                    create=True,
                )
            if rfile and wfile:
                shutil.copyfileobj(rfile, wfile)
                BLOBManager.Close(rfile)
                BLOBManager.Close(wfile)
            self.log.info(
                'Defaults file copied from template user OGo#{0} '
                'to new account OGo#{1}'
                .format(self.template_id, self.obj.object_id, )
            )
