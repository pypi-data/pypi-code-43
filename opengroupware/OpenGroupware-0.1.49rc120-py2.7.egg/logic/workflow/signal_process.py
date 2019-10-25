#
# Copyright (c) 2010, 2015
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
from coils.core import \
    Command, \
    OGO_ROLE_SYSTEM_ADMIN, \
    OGO_ROLE_WORKFLOW_ADMIN, \
    AccessForbiddenException


class SignalProcess(Command):
    __domain__ = "process"
    __operation__ = "signal"

    def check_run_permissions(self):
        if (
            self._ctx.has_role(OGO_ROLE_SYSTEM_ADMIN) or
            self._ctx.has_role(OGO_ROLE_WORKFLOW_ADMIN)
        ):
            return

        rights = self._ctx.access_manager.access_rights(self.obj, )
        if set('wp').intersection(rights):
            return

        raise AccessForbiddenException(
            'Insufficient privileges to signal process OGo#{0}'
            .format(self.obj.object_id, )
        )

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.obj = params.get('process', params.get('object', None))
        self._context_id = params.get('runas', self._ctx.account_id)
        self._callback = params.get('callback', None)

    def run(self):
        self._result = self._ctx.send(
            None,
            'coils.workflow.executor/start',
            {
                'processId': self.obj.object_id,
                'contextId': self._context_id,
            },
            callback=self._callback,
        )
