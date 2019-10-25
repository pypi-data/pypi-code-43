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
# THE SOFTWARE.
#
import json
from StringIO import StringIO
from coils.foundation import coils_json_encode
from coils.core import \
    CoilsException, \
    ObjectProperty, \
    AccessForbiddenException
from pathobject import PathObject


class ObjectPropertyPOST(PathObject):

    def __init__(self, parent, name, **params):
        self.name = name
        PathObject.__init__(self, parent, **params)

    def do_HEAD(self):
        self.request.simple_response(
            201,
            mimetype='application/json',
            headers={
                'Content-Length': '0',
                'ETag': '{0}:{1}'.format(
                    self.entity.object_id,
                    self.entity.version,
                ),
                'X-OpenGroupware-ObjectId': str(self.entity.object_id),
            }
        )

    def do_POST(self):

        mimetype = self.request.headers.get('Content-Type', None)
        if mimetype not in ('application/json', ):
            raise CoilsException(
                'ObjectPropertyPOST payload must have MIME-type '
                '"application/json"'
            )

        payload = self.request.get_request_payload()
        # Parse payload
        values = json.loads(payload)
        # Get entityName from payload
        if not isinstance(values, dict):
            raise CoilsException(
                'ObjectPropertyPOST payload must be a dictionary.'
            )

        rights = self.context.access_manager.access_rights(self.entity, )
        if not set('w').intersection(rights):
            raise AccessForbiddenException(
                'Insufficient access to OGo#{0}; write permissions required.'
                .format(self.entity.object_id, )
            )

        for key, value in values.items():
            ns, attribute = ObjectProperty.Parse_Property_Name(key)
            self.context.property_manager.set_property(
                entity=self.entity,
                namespace=ns,
                attribute=attribute,
                value=value,
            )

        self.context.commit()

        response = dict()
        for prop in self.context.property_manager.get_properties(self.entity):
            response[
                '{{{0}}}{1}'.format(prop.namespace, prop.name, )
            ] = (
                prop.get_hint(),
                prop.get_value(),
                prop.access_id if prop.access_id else 0,
            )
        response_stream = StringIO()
        coils_json_encode(response, response_stream)
        response = None

        self.request.simple_response(
            200,
            stream=response_stream,
            mimetype=u'application/json; charset=utf-8',
            headers={
                'X-OpenGroupware-ObjectId': self.entity.object_id,
                'etag': '{0}:{1}'.format(
                    self.entity.object_id,
                    self.entity.version,
                ),
            },
        )
