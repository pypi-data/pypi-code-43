#
# Copyright (c) 2011, 2013, 2014, 2016
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
import json
import datetime
import time
from coils.net import PathObject, Protocol
from coils.core.omphalos import Render as Omphalos_Render


MAX_VISTA_CANDIDATES = 2048


def omphalos_encode(o):
    if (isinstance(o, datetime.datetime)):
        return o.strftime('%Y-%m-%dT%H:%M:%S')
    raise TypeError()


class VistaSearch(Protocol, PathObject):
    __pattern__ = '^vista$'
    __namespace__ = None
    __xmlrpc__ = False

    def __init__(self, parent, **params):
        PathObject.__init__(self, parent, **params)

    def get_name(self):
        return 'vista'

    def is_public(self):
        return False

    def do_HEAD(self):
        """
        Generate HEAD response, here for technical completeness.
        A head request here is sfunctionally useless.
        """
        self.request.simple_response(
            200,
            data=None,
            mimetype=self.entity.get_mimetype(type_map=self._mime_type_map),
            headers={'etag': 'vista-search', },
        )

    def do_GET(self):
        """
        Perform a Vista search using URL parameters as the criteria
        Parameters:
          term - a search term
          archived - if present arhived entities are included in the search
          workflow - if present Workflow entities are included in the search
          type - constraint of type of entities to be included in the search
          limit - maximum number of objects to return from the search
          project - object id of a project in order to scope the search
        Both "type" and "term" may be specified multiple times
        """

        possible_object_ids = list()

        include_archived = 'archived' in [x.lower() for x in self.parameters]

        include_workflow = 'workflow' in [x.lower() for x in self.parameters]

        if 'type' in self.parameters:
            entity_types = [
                'document'
                if x.lower() == 'file'
                else x.lower()
                for x in self.parameters['type']
            ]
        else:
            entity_types = None

        search_limit = self.parameters.get('limit', [100, ])
        search_limit = int(search_limit[0])
        if search_limit > MAX_VISTA_CANDIDATES:
            search_limit = MAX_VISTA_CANDIDATES

        if 'term' in self.parameters:
            keywords = [
                x.lower().replace(' ', '\ ')
                for x in self.parameters['term']
            ]
            for keyword in keywords:
                if keyword.isdigit():
                    possible_object_ids.append(long(keyword))
        else:
            keywords = [self.context.login, ]

        project_id = None
        if 'project' in self.parameters:
            value = [long(x) for x in self.parameters['project']]
            if value:
                project_id = value[0]

        detail_level = self.parameters.get('detail', None)
        if detail_level:
            detail_level = int(detail_level[0])
        else:
            # comment + company values
            detail_level = 2056

        start = time.time()
        if project_id:
            # Perform Vista search scoped by a Project
            results = self.context.run_command(
                'vista::search',
                keywords=keywords,
                entity_types=entity_types,
                search_limit=0,
                project_id=project_id,
                include_workflow=include_workflow,
                include_archived=include_archived,
            )
        else:
            # Perform unscoped Vista search
            results = self.context.run_command(
                'vista::search',
                keywords=keywords,
                entity_types=entity_types,
                search_limit=0,
                include_workflow=include_workflow,
                include_archived=include_archived,
            )

        end = time.time()
        self.context.send(
            None,
            'coils.administrator/performance_log',
            {
                'lname': 'vista',
                'oname': 'query',
                'runtime': (end - start),
                'error': False,
            }
        )

        # We return the number of original results to the client, but we
        # trim the 'rendered' results to less than 100
        result_count = len(results)
        if len(results) > search_limit:
            results = results[:search_limit]

        if possible_object_ids:
            """
            attempt a direct object id lookup for all keywords with were
            recorded as numeric - isdigit() - attempting to use these values
            as object ids.
            """
            for object_id in possible_object_ids:
                object_result = self.context.tm.get_entity(object_id)
                if object_result and object_result not in results:
                    results.insert(0, object_result)

        start = time.time()
        results = Omphalos_Render.Results(
            results, detail_level, self.context,
        )
        results = json.dumps(results, default=omphalos_encode)
        end = time.time()
        self.context.send(
            None,
            'coils.administrator/performance_log',
            {
                'lname': 'vista',
                'oname': 'render',
                'runtime': (end - start),
                'error': False,
            }
        )

        self.request.simple_response(
            200,
            mimetype='text/plain',
            headers={
                'X-OpenGroupware-Coils-Vista-Matches': str(result_count),
            },
            data=results,
        )
