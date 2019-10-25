# Copyright (c) 2009, 2014
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
# THE SOFTWARE.
#
from coils.core import \
    Command, CoilsException, UserDefaultsManager, AccessForbiddenException


class SetDefaults(Command):
    __domain__ = "account"
    __operation__ = "set-defaults"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):

        self._defaults = params.get('defaults', None)
        if not self._defaults:
            raise CoilsException(
                'No defaults provided to {0}'.format(self.command_name(), )
            )

        if 'id' in params:
            self._account_id = int(params['id'])
        elif 'login' in params:
            account = self._ctx.run_command(
                'account::get', login=params['login'],
            )
            self._account_id = account.object_id
        else:
            self._account_id = self._ctx.account_id

    def check_run_permissions(self):
        if self._account_id == self._ctx.account_id:
            return
        if self._ctx.is_admin:
            return
        if self._account_id in self._ctx.context_ids:
            return
        raise AccessForbiddenException(
            'Account {0} not permitted to modify defaults of account {1}'
            .format(self._ctx.account_id, self._account_id, )
        )

    def run(self):
        ud = UserDefaultsManager(self._account_id)
        self.log.debug(
            'Updating account defaults for OGo#{0}'.format(self._account_id, )
        )
        ud.update_defaults(self._defaults)
        ud.sync()
        self.set_result(ud.defaults())
