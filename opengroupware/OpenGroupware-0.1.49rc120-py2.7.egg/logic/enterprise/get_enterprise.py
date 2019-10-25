#
# Copyright (c) 2009, 2012, 2015
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
# THE SOFTWARE
#
import time
from sqlalchemy import and_
from coils.core import Enterprise
from coils.foundation import apply_orm_hints_to_query
from coils.logic.address import GetCompany


class GetEnterprise(GetCompany):
    __domain__ = "enterprise"
    __operation__ = "get"

    def __init__(self):
        GetCompany.__init__(self)

    def run(self, **params):
        db = self._ctx.db_session()
        if (len(self.object_ids) == 0):
            # Bail out of there are no ids specified
            self.set_return_value([])
            return
        query = db.query(Enterprise).filter(
            and_(
                Enterprise.object_id.in_(self.object_ids),
                Enterprise.status != 'archived',
            )
        )
        query = apply_orm_hints_to_query(query, Enterprise, self.orm_hints)
        query_start = time.time()
        data = query.all()
        self.log.debug(
            'Enterprise query by id retrieved {0} entries in {1}s.'
            .format(len(data), time.time() - query_start, )
        )
        self.set_return_value(data)
