#
# Copyright (c) 2015
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
from datetime import timedelta
from coils.core import \
    AuthenticationToken, \
    Command, \
    OGO_ROLE_SYSTEM_ADMIN, \
    AccessForbiddenException
from coils.core.logic import DeleteCommand
from command import TokenCommand

"""
class AuthenticationToken(Base, KVC):
    __tablename__ = 'login_token'
    __entityName__ = 'AuthenticationToken'
    __internalName__ = 'AuthenticationToken'
    token : String
    account_id : Integer
    created : DateTime
    touched : DateTime
    environment : String
    expiration : DateTime
    server_name : String
    timeout : Integer
"""


class ExpireTokens(Command, TokenCommand):
    __domain__ = "token"
    __operation__ = "expire"

    def prepare(self, ctx, **params):
        Command.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)
        self.overkeep = int(params.get('overkeep', 0))

    def check_run_permissions(self):
        if self._ctx.has_role(OGO_ROLE_SYSTEM_ADMIN):
            return
        raise AccessForbiddenException(
            'Context lacks administrative role; cannot expire attachments.'
        )

    def run(self):

        expires_time = (
            self._ctx.get_utctime() - timedelta(seconds=self.overkeep)
        )

        query = (
            self._ctx.db_session().
            query(AuthenticationToken).
            filter(AuthenticationToken.expiration < expires_time)
        )

        tokens = query.all()

        counter = 0

        for token in tokens:
            self._ctx.run_command('token::delete', token=token, )
            counter += 1

        self.log.info(
            '{0} athentication tokens deleted due to expiration'
            .format(counter, )
        )

        self.set_result(counter)
