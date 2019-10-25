#
# Copyright (c) 2014, 2015
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
from coils.core import CoilsException
from coils.foundation import Process
from coils.core.logic import SearchCommand
from keymap import COILS_PROCESS_KEYMAP


class SearchProcesses(SearchCommand):
    __domain__ = "process"
    __operation__ = "search"
    mode = None

    def __init__(self):
        SearchCommand.__init__(self)

    def prepare(self, ctx, **params):
        SearchCommand.prepare(self, ctx, **params)

    def parse_parameters(self, **params):
        SearchCommand.parse_parameters(self, **params)

    def _custom_key_route_name(self, key, value, conjunction, expression, ):
        """
        Expand route names in search criteria into an IN(LIST) search
        clause.
        """

        # TODO: Add support for expression "IN"

        if (
            expression not in (
                'EQUALS', 'NOTEQUALS', 'LIKE', 'ILIKE',
            )
        ):
            raise CoilsException(
                'Unsupported expression "{0}"for search key '
                '"routeName", expression must be one of EQUALS, '
                'NOTEQUALS, LIKE or ILIKE'.format(expression, )
            )

        if not isinstance(value, basestring):
            raise CoilsException(
                'Value of search key "routeName" is of type "{1}", '
                'value required to be a string'.format(type(value), )
            )

        routes = self._ctx.run_command(
            'route::search',
            criteria={
                'key': 'name',
                'value': value,
                'expression': expression,
            },
        )
        if routes:
            route_ids = [r.object_id for r in routes]
            self.log.debug(
                'Discovered {0} route(s) for name "{1}"'
                .format(len(route_ids), value, )
            )
            return (
                Process,
                'route_id',
                route_ids,
                conjunction,
                'IN',
            )
        else:
            self.log.warn(
                'Unable to determine route object id for route named "{0}"'
                .format(value, )
            )
            """
            there will never be an object id 1 so we will return that as
            value for the criteria.  this allows this clause to still
            perform as expected in an OR clause - it evaluate to False
            """
            return (
                Process,
                'route_id',
                1,
                conjunction,
                expression,
            )

    def _custom_search_criteria(self, key, value, conjunction, expression, ):

        """
        WARN: this will break any attempt to implement support for
        expression IN
        """
        key = key[0]  # key is provided as a list

        if key in ('route_name', ):
            return self._custom_key_route_name(
                key, value, conjunction, expression,
            )

        if key in ('group_name', ):
            """
            translate the group_name in to the object id of the RouteGroup.
            then we all through to the custom key process for group_id
            """
            # TODO: Add support for wildcard searching of group name
            key = 'group_id'
            group = self._ctx.run_command('routegroup::get', name=value, )
            if group:
                value = group.object_id
            else:
                value = 1

        if key in ('group_id', ):
            # TODO: implement support for IN expression
            routes = self._ctx.run_command('route::get', group_id=value, )
            route_ids = [route.object_id for route in routes]
            routes = None
            if route_ids:
                """
                We want to avoid generating an empty IN cluase as doing so will
                (1) cause SQLAlchemy to bark warnings into the logs and (2) may
                confuse PostgreSQL's query opimizer.  So this key will be
                dropped out as an undefined key if the route_ids list is empty.
                """
                return (
                    Process,
                    'route_id',
                    route_ids,
                    conjunction,
                    'IN',
                )

        # unsupported custom key

        return (None, None, None, None, None, )

    def add_result(self, process):
        if (process not in self._result):
            self._result.append(process)

    def _get_search_keymap(self):
        keymap = COILS_PROCESS_KEYMAP.copy()
        keymap.update(
            {
                'uuid':          ['uuid', 'str', None, ],
                'priority':      ['priority', 'int', None, ],
                'status':        ['status', 'string', None, ],
                'state':         ['state', 'str', None, ],
                'task_id':       ['task_id', 'int', None, ],
                'taskid':        ['task_id', 'int', None, ],
                'taskobjectid':  ['task_id', 'int', None, ],
                'ownerid':       ['owner_id', 'int', None, ],
                'owner_id':      ['owner_id', 'int', None, ],
                'ownerobjectid': ['owner_id', 'int', None, ],
                'created':       ['created', 'date', None, ],
                'modified':      ['modified', 'date', None, ],
                'parked':        ['parked', 'date', None, ],
                'completed':     ['completed', 'date', None, ],
                'route_name':    ['route_name', 'string', None, ],
                'routename':     ['route_name', 'string', None, ],
                'route_group_id': ['group_id', 'int', None, ],
                'routegroupid':  ['group_id', 'int', None, ],
                'routegroupobjectid': ['group_id', 'int', None, ],
                'routegroupname': ['group_name', 'string', None, ],
                'route_group_name': ['group_name', 'string', None, ],
            }
        )
        return keymap

    def run(self):
        self._query = self._parse_criteria(
            self._criteria,
            Process,
            self._get_search_keymap(),
        )
        data = self._query.all()
        self.log.debug('query returned {0} objects'.format(len(data), ))
        self.set_return_value(data)
        return
