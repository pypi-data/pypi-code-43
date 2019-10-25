#
# Copyright (c) 2017
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
from .workflow_map import WorkflowMap
from .standard_xml_to_hierarchic_map import StandardXMLToHierarchicMap
from .exceptions import NoSuchMapClassException, \
    MapClassInitializationException
from coils.foundation import \
    coils_yaml_encode, \
    coils_yaml_encode_to_string, \
    coils_yaml_decode


WORKFLOW_MAP_CLASS = {
    'StandardXMLToHierarchicMap': StandardXMLToHierarchicMap,
}


class MapFactory(object):

    @staticmethod
    def Marshall(context, name):
        map_document = WorkflowMap.Load(name)
        context.log.debug('Workflow map document loaded for map "{0}"'.format(name, ))  # noqa
        return MapFactory.MarshallFromMap(context, map_document, name=name)

    @staticmethod
    def MarshallFromName(context, name):
        return MapFactory.Marshall(context, name)

    @staticmethod
    def MarshallFromText(context, map_document):
        map_document = coils_yaml_decode(map_document, allow_none=True, )
        return MapFactory.MarshallFromMap(context, map_document, )

    @staticmethod
    def MarshallFromMap(context, map_document, name=None):
        if 'class' not in map_document:
            classname = 'StandardXMLToHierarchicMap'
        else:
            classname = map_document['class']
        map_class = WORKFLOW_MAP_CLASS.get(classname, None)
        if not map_class:
            context.log.debug('No such Map class as {0}'.format(classame, ))  # noqa
            raise NoSuchMapClassException(
                'No such Map class as "{0}"'
                .format(classname, )
            )
        if name:
            context.log.debug('Class {0} selected for map '.format(map_class, name, ))  # noqa
        else:
            context.log.debug('Class {0} selected for unnamed map '.format(map_class, ))  # noqa
        try:
            instance = map_class(context, map_document=map_document)
        except Exception as exc:
            context.log.exception(exc)
            raise MapClassInitializationException(inner_exception=exc, )
        instance.name = name
        return instance
