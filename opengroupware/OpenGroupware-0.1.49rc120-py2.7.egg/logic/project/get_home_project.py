#!/usr/bin/python
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
# THE SOFTWARE.
#
from sqlalchemy import and_
from coils.core import \
    Project
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from coils.core.logic import GetCommand
from coils.foundation import apply_orm_hints_to_query


class GetHomeProject(GetCommand):
    __domain__ = "project"
    __operation__ = "get-home-project"
    mode = None

    def __init__(self):
        GetCommand.__init__(self)

    def parse_parameters(self, **params):
        GetCommand.parse_parameters(self, **params)

    def run(self, **params):

        if self._ctx.account_id < 10001:
            """System accounts do not have home projects"""
            self.set_return_value(None)
            return

        db = self._ctx.db_session()
        account_id = self._ctx.account_id
        kind = '::coils:cabinet:home:{0}'.format(account_id, )
        query = db.query(Project).\
            filter(
                and_(
                    Project.is_fake == 1,
                    Project.kind == kind,
                    Project.status != 'archived'
                )
            )
        apply_orm_hints_to_query(query, Project, self.orm_hints)
        try:
            project = query.one()
        except NoResultFound:
            # auto create?
            self.set_return_value(None)
            return
        except MultipleResultsFound:
            # log error about multiple results
            self.set_return_value(None)
            return

        self.set_single_result_mode()
        self.set_return_value(project, right='l')
