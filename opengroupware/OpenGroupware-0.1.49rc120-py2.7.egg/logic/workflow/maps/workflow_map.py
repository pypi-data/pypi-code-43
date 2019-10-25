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
# THE SOFTWARE
#
from datetime import datetime
from coils.foundation import \
    coils_yaml_encode, \
    coils_yaml_encode_to_string, \
    coils_yaml_decode
from coils.core import BLOBManager, CoilsException
from .exceptions import MapClassInitializationException


def get_standardxml_type_name(value):
    if isinstance(value, int) or isinstance(value, long):
        return 'integer'
    if isinstance(value, basestring):
        return 'string'
    if isinstance(value, float):
        return 'float'
    if isinstance(value, datetime):
        return 'datetime'
    return 'unknown'


class WorkflowMap(object):

    def __init__(self, ctx, map_document=None, ):
        self._context = ctx
        self._map_document = map_document
        self._rfile = None
        self._wfile = None

    @property
    def rfile(self):
        return self._rfile

    @property
    def wfile(self):
        return self._wfile

    @staticmethod
    def Save(name, data):
        """
        Save the map document (probably a dict) as the specified name.  The
        save call will cook the document into a YAML document.
        """
        if name.endswith('.yaml'):
            name = name[:-len('.yaml')]
        wfile = BLOBManager.Create(
            'wf/maps/{0}.yaml'.format(name, ),
            encoding='binary',
        )
        if wfile is None:
            raise CoilsException(
                'Unable to open Workflow Map "{0}"'.format(name, )
            )
        coils_yaml_encode(data, wfile, allow_none=True, )
        wfile.close()

    @staticmethod
    def Load(name):
        """
        Load the named WorkFlowMap, this returns the map document, probably a
        dict, it is not cooked into a WorkflowMap instance (yet).  The load
        call decodes the 'raw' document from YAML.
        """
        if name.endswith('.yaml'):
            name = name[:-len('.yaml')]
        rfile = BLOBManager.Open(
            'wf/maps/{0}.yaml'.format(name, ),
            'rb',
            encoding='binary',
        )
        if not rfile:
            raise MapClassInitializationException(
                'Unable to load map description "{0}" from filesystem'.format(name, )  # noqa
            )
        data = coils_yaml_decode(rfile, allow_none=True, )
        rfile.close()
        return data

    @staticmethod
    def List():
        """
        List the defined workflow maps as a list of names.  These are the files
        in the $ROOT/wf/maps/ folder.  The file suffix of the name ends in
        ".yaml" the suffix is stripped from the name.
        """
        result = list()
        for name in BLOBManager.List('wf/maps/'):
            if name.endswith('.yaml'):
                name = name[:-len('.yaml')]
            result.append(name)
        return result

    @staticmethod
    def Delete(name):
        if name.endswith('.yaml'):
            name = name[:-len('.yaml')]
        return BLOBManager.Delete('wf/maps/{0}.yaml'.format(name, ))

    def load(self, name):
        data = WorkflowMap.Load(name, )
        self._map_document = data

    def save(self, name):
        WorkflowMap.Save(name, self._map_document)

    def run(self, rfile, wfile):
        pass

    def close(self):
        pass

    def verify_input(self, mimetype):
        return True

    @property
    def map_document(self):
        """
        Returns the decoded map document, probably a dict.
        """
        return self._map_document

    @property
    def result_mimetype(self):
        """
        The type of content resulting from a successful invocation of the map
        """
        return 'application/xml'

    @property
    def mimetype(self):
        return self.file_mimetype

    @property
    def file_mimetype(self):
        """
        The MIME type of the map when presented to clients, typically this
        is via WebDAV
        """
        return 'text/x-yaml'

    @property
    def file_extention(self):
        if self.mimetype == 'text/x-yaml':
            return 'yaml'
        raise CoilsException('Non-YAML Workflow Map cannot be represented')

    @property
    def file_size(self):
        """
        Return the size of the YAML representation of the map, typically this
        is used via WebDAV
        """
        if self.mimetype == 'text/x-yaml':
            return len(self.yaml_document)
        raise CoilsException('Non-YAML Workflow Map cannot be represented')

    @property
    def yaml_document(self):
        """
        Returns the YAML representation of the map document
        """
        if self.mimetype == 'text/x-yaml':
            return coils_yaml_encode_to_string(self._map_document)
        raise CoilsException('Non-YAML Workflow Map cannot be represented')
