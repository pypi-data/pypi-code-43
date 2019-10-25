
from coils.core import CoilsException
from coils.logic.workflow.maps import WorkflowMap, StandardXMLToHierarchicMap
from .exceptions import NoSuchMapClassException, \
    MapClassInitializationException


WORKFLOW_MAP_CLASS = {
    'StandardXMLToHierarchicMap': StandardXMLToHierarchicMap,
}


class MapFactory(object):

    @staticmethod
    def Marshall(context, name):
        map_document = WorkflowMap.Load(name)
        if 'class' not in map_document:
            classname = 'StandardXMLToHierarchicMap'
        else:
            classname = map_document['class']
        map_class = WORKFLOW_MAP_CLASS.get(classname, None)
        if not map_class:
            raise NoSuchMapClassException(
                'No such Map class as "{0}"'
                .format(classname, )
            )
        instance = map_class(context, map_document=map_document)
        instance.name = name
        return instance


