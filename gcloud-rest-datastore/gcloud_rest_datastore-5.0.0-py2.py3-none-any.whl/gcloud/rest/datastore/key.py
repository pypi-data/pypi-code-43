from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import str
from future import standard_library
standard_library.install_aliases()
from builtins import object
from typing import Any
from typing import Dict
from typing import List
from typing import Optional


class PathElement(object):
    def __init__(self, kind     , **_3to2kwargs)        :
        if 'name' in _3to2kwargs: name = _3to2kwargs['name']; del _3to2kwargs['name']
        else: name =  None
        if 'id_' in _3to2kwargs: id_ = _3to2kwargs['id_']; del _3to2kwargs['id_']
        else: id_ =  None
        self.kind = kind

        self.id = id_
        self.name = name
        if self.id and self.name:
            raise Exception('invalid PathElement contains both ID and name')

    def __eq__(self, other     )        :
        if not isinstance(other, PathElement):
            return False

        return bool(self.kind == other.kind and self.id == other.id
                    and self.name == other.name)

    def __repr__(self)       :
        return str(self.to_repr())

    @classmethod
    def from_repr(cls, data                )                 :
        kind      = data['kind']
        id_                = data.get('id')
        name                = data.get('name')
        return cls(kind, id_=id_, name=name)

    def to_repr(self)                  :
        data                 = {'kind': self.kind}
        if self.id:
            data['id'] = self.id
        elif self.name:
            data['name'] = self.name

        return data


class Key(object):
    path_element_kind = PathElement

    def __init__(self, project     , path                   ,
                 namespace      = '')        :
        self.project = project
        self.namespace = namespace
        self.path = path

    def __eq__(self, other     )        :
        if not isinstance(other, Key):
            return False

        return bool(self.project == other.project
                    and self.namespace == other.namespace
                    and self.path == other.path)

    def __repr__(self)       :
        return str(self.to_repr())

    @classmethod
    def from_repr(cls, data                )         :
        return cls(data['partitionId']['projectId'],
                   path=[cls.path_element_kind.from_repr(p)
                         for p in data['path']],
                   namespace=data['partitionId'].get('namespaceId', ''))

    def to_repr(self)                  :
        return {
            'partitionId': {
                'projectId': self.project,
                'namespaceId': self.namespace,
            },
            'path': [p.to_repr() for p in self.path],
        }
