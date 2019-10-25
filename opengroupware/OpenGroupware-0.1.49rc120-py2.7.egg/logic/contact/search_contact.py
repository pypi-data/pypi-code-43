#
# Copyright (c) 2009, 2013, 2015, 2016
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
import time
from coils.foundation import apply_orm_hints_to_query, CompanyAssignment
from coils.core import Contact, CoilsException
from coils.logic.address import SearchCompany
from keymap import COILS_CONTACT_KEYMAP

"""
Input:
    criteria = [
        {
            'value':,
            'conjunction':,
            'key':,
            'expression': EQUALS | LIKE | ILIKE,
        } ...
    ]
    limit = #
    debug = True / False
    access_check = True / False
"""


class SearchContacts(SearchCompany):
    __domain__ = "contact"
    __operation__ = "search"
    mode = None

    def __init__(self):
        SearchCompany.__init__(self)

    def prepare(self, ctx, **params):
        SearchCompany.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        SearchCompany.parse_parameters(self, **params)

    def add_result(self, contact):
        if (contact not in self._result):
            self._result.append(contact)

    def _custom_search_criteria(self, key, value, conjunction, expression, ):

        if len(key) > 1:
            # No compound custom keys supported
            return (None, None, None, None, None, )

        key = key[0]
        if key == 'memberof' and expression == 'EQUALS':
            query = None
            if isinstance(value, basestring):
                """
                value is a string, either a numeric string which is an
                object id or it must be the name of a team.
                """
                if value.isdigit():
                    query = self._ctx.db_session().query(
                        CompanyAssignment
                    ).filter(CompanyAssignment.parent_id == int(value))
                else:
                    team = self._ctx.run_command('team::get', name=value, )
                    if not team:
                        raise CoilsException(
                            'memberof value "{0}" does not identity a team'
                            .format(value, )
                        )
                    query = self._ctx.db_session().query(
                        CompanyAssignment
                    ).filter(CompanyAssignment.parent_id == team.object_id)
            elif isinstance(value, int):
                """
                value is an integer, assuming this is an object id of either
                and enterprise or a team and using it as-is.
                """
                query = self._ctx.db_session().query(
                    CompanyAssignment
                ).filter(CompanyAssignment.parent_id == value)
            if query is None:
                raise CoilsException(
                    'Unable to construct memeberof expression '
                    'using value "{0}" or type "{1}"'
                    .format(value, type(value), )
                )
            member_ids = [x.child_id for x in query.all()]
            return (Contact, 'object_id', member_ids, conjunction, 'IN', )

        # unsupported custom key
        return (None, None, None, None, None, )

    def do_revolve(self):
        enterprises = list()
        for contact in self._result:
            enterprises.extend(
                [assignment.parent_id for assignment in contact.enterprises]
            )
        return self._ctx.run_command(
            'enterprise::get',
            ids=set(enterprises),
            orm_hints=self.orm_hints,
        )

    def run(self):
        self._query = self._parse_criteria(
            self._criteria, Contact, COILS_CONTACT_KEYMAP,
        )
        self._query = \
            apply_orm_hints_to_query(self._query, Contact, self.orm_hints, )
        query_start = time.time()
        data = self._query.all()
        self.log.debug(
            'search query returned {0} objects in {1}s'
            .format(len(data), time.time() - query_start, )
        )
        self.set_return_value(data)
        return
