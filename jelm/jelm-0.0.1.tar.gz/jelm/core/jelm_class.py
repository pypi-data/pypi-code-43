import json

from typing import Optional, Union


class Edge:

    def __init__(self,
                 source: str,
                 target: str,
                 id: Optional[str] = None,
                 attributes: Optional[dict] = None):

        self.source = source
        self.target = target
        self.id = id
        self.attributes = attributes or {}

    def get_dict(self) -> dict:
        optionals = {
            k: self.__getattribute__(k)
            for k in ['id', 'attributes'] if self.__getattribute__(k)
        }
        return {
            'type': 'edge',
            'source': self.source,
            'target': self.target,
            **optionals
        }


class Node:

    def __init__(self,
                 id: str,
                 attributes: Optional[dict] = None):
        self.id = id
        self.attributes = attributes or {}

    def get_dict(self) -> dict:
        if self.attributes:
            optionals = {'attributes': self.attributes}
        else:
            optionals = {}
        return {
            'type': 'edge',
            'id': self.id,
            **optionals
        }


class Jelm:

    def __init__(self,
                 metadata: Optional[dict]=None,
                 objects: Optional[list]=None,
                 **kwargs):

        self.metadata = metadata or {}
        self.objects = objects or []

        if kwargs:
            raise ValueError("Tried to create jelm object with additional kwargs {}"
                             .format(kwargs.keys()))

    def get_dict(self) -> dict:
        return {
            'metadata': self.metadata,
            'objects': self.objects
        }

    def get_json(self) -> str:
        return json.dumps(self.get_dict())

    def add_object(self, obj: Union[dict, Edge, Node]):

        if isinstance(obj, dict):

            try:
                obj_type = obj.pop('type')
            except KeyError:
                raise ValueError("if dict is given, 'type' key needs to be set! (to either node or edge)")

            if obj_type == 'edge':
                parsed_obj = Edge(**obj).get_dict()
            elif obj_type == 'node':
                parsed_obj = Node(**obj).get_dict()
            else:
                raise ValueError("object type needs to be either node or edge it is {}".format(obj_type))
        else:
            parsed_obj = obj.get_dict()

        self.objects.append(parsed_obj)

    def add_edge(self,
                 source: str,
                 target: str,
                 id: Optional[str] = None,
                 attributes: Optional[dict] = None):

        parsed_obj = Edge(source,
                          target,
                          id,
                          attributes).get_dict()
        self.objects.append(parsed_obj)

    def add_node(self,
                 id: str,
                 attributes: Optional[dict] = None):

        parsed_obj = Node(id, attributes).get_dict()

        self.objects.append(parsed_obj)