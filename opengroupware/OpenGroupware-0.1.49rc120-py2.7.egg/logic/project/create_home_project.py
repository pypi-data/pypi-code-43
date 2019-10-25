#
# Copyright (c) 2016
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
from coils.core import Command


class CreateHomeProject(Command):
    __domain__ = "project"
    __operation__ = "new-home-project"

    def prepare(self, ctx, **params):
        Command.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        Command.parse_parameters(self, **params)

    def run(self):

        if self._ctx.account_id < 10001:
            """System accounts do not have home projects"""
            self.set_return_value(None)
            return

        home = self._ctx.run_command('project::get-home-project', )
        if home:
            self.set_return_value(home)
        values = {
            'isFake': 1,
            'kind': '::coils:cabinet:home:{0}'.format(self._ctx.account_id, ),
            'name': '{0} home'.format(self._ctx.get_login(), ),
        }
        home = self._ctx.run_command(
            'project::new', values=values,
        )
        self.set_return_value(home)
