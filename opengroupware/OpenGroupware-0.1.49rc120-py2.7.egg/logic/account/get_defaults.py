# Copyright (c) 2009, 2014
#   Adam Tauno Williams <awilliam@whitemice.org>
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
from coils.core import Command, UserDefaultsManager, AccessForbiddenException


class GetDefaults(Command):
    __domain__ = "account"
    __operation__ = "get-defaults"

    def __init__(self):
        Command.__init__(self)

    def parse_parameters(self, **params):
        if 'id' in params:
            self._account_id = long(params.get('id'))
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
            'Account {0} not permitted to read defaults of account {1}'
            .format(self._ctx.account_id, self._account_id, )
        )

    def run(self, **params):
        self.log.debug(
            'Loading account defaults for OGo#{0}'.format(self._account_id, )
        )
        self.set_result(UserDefaultsManager(self._account_id).defaults())
