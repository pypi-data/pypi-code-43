#
# Copyright (c) 2015, 2017
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
from datetime import datetime
from coils.net import DAVObject


class MapObject(DAVObject):

    def __init__(self, parent, name, **params):
        DAVObject.__init__(self, parent, name, **params)
        self._map_text = None

    def _get_map_text(self):
        if not self._map_text:
            self._map_text = self.entity.yaml_document
        return self._map_text

    def get_property_webdav_getetag(self):
        return '{0}:{1}'.format(
            self.entity.name,
            self.get_property_webdav_modifieddate(),
        )

    def get_property_webdav_displayname(self):
        return self.entity.name

    def get_property_webdav_getcontentlength(self):
        return str(self.entity.file_size)

    def get_property_webdav_creationdate(self):
        # TODO: Implement
        return datetime.now()
        return self.entity.created

    def get_property_webdav_modifieddate(self):
        # TODO: Implement
        return datetime.now()
        return self.entity.modified

    def do_HEAD(self):
        self.request.simple_response(
            201,
            mimetype=self.entity.mimetype,
            headers={
                'Content-Length': str(self.entity.size),
                'ETag': self.get_property_webdav_getetag(),
            },
        )

    def do_GET(self):
        self.request.simple_response(
            200,
            data=self.entity.yaml_document,
            mimetype=self.entity.file_mimetype,
            headers={
                'etag': self.get_property_webdav_getetag(),
            },
        )
