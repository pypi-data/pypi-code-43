"""
An interface with a schema repository
"""

import jsonref
from . import entity


class Schema_Store(object):


    def __init__(self, getter, saver):
        self.getter = getter
        self.saver = saver


    def get_schema(self, uri, **kwargs):
        """ Return a schema quering the store with the given uri"""
        return self.getter(uri, **kwargs)


    def get_object(self, uri, **kwargs):
        """ Return an entity.Object quering the store with the given uri"""
        return entity.Object(schema = self.get_schema(uri))


    def resolve(self, schema, **kwargs):
        result = jsonref.JsonRef.replace_refs(schema, loader=self.get_schema)
        return result


    def save(self, entity, **kwargs):
        return self.saver(entity.schema)
