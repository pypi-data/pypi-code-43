import json
import re

from enum import Enum


class AttributeDict(dict):

    def __init__(self, seq=None, **kwargs):
        if seq:
            super().__init__(seq, **kwargs)

    def __getattr__(self, key):
        if key in self:
            return self[key]
        elif key.startswith('__') and key.endswith('__'):
            raise AttributeError('Key not found: ' + key)
        else:
            return None

    def __setattr__(self, key, value):
        self[key] = value


class Document:
    """
    A Document is the base representation of an unstructured source object, it consists of
    metadata and then a content object
    """

    def __init__(self, metadata, content):
        self.metadata = metadata
        self.content = content

    def to_dict(self):
        return json.loads(json.dumps({"metadata": self.metadata, "content": self.content}))


class DocumentMetadata(AttributeDict):
    """
    Document metadata is simply a collection of metadata about a document
    """


class ContentNode(AttributeDict):
    """
    A simple structure for holding a content node, this is any structure which can have both a value
    and metadata, where the metadata can include spatial layout, structural information and the value is the text
    content itself
    """

    def __init__(self, seq=None, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.children = []
        self.features = AttributeDict()

    def count(self):
        """
        Count the total number of nodes under this node
        :return: total number of nodes
        """
        cnt = 0
        for child in self.children:
            cnt += 1
            cnt += child.count()

        return cnt


class FindDirection(Enum):
    CHILDREN = 1
    PARENT = 2


class QueryableNode:
    """
    A wrapped around a ContentNode that provides query and navigation interfaces
    """

    def __init__(self, parent, node, index):
        self.node = node
        self.parent = parent
        self.index = index
        self.children = []

    def count(self):
        """
        Count the total number of nodes under this node
        :return: total number of nodes
        """
        return self.node.count()

    def findall(self, value_re=".*", type_re=".*", direction=FindDirection.CHILDREN):
        """
        Search for a node that matches on the value and or type using
        regular expressions
        """
        value_compiled = re.compile(value_re)
        type_compiled = re.compile(type_re)
        return self.findall_compiled(value_compiled, type_compiled, direction)

    def findall_compiled(self, value_re_compiled, type_re_compiled, direction):
        """
        Search for a node that matches on the value and or type using
        regular expressions using compiled expressions
        """
        hits = []
        value = "" if not self.get_value() else self.get_value()

        if value_re_compiled.match(value) and type_re_compiled.match(self.get_type()):
            hits.append(self)

        if direction is FindDirection.CHILDREN:
            for child in self.children:
                hits.extend(child.findall_compiled(value_re_compiled, type_re_compiled, direction))
        else:
            if self.parent:
                hits.extend(self.parent.findall_compiled(value_re_compiled, type_re_compiled, direction))

        return hits

    def get_x(self):
        return self.node['bbox'][0]

    def get_y(self):
        return self.node['bbox'][1]

    def get_width(self):
        return self.node['bbox'][2] - self.node['bbox'][0]

    def get_height(self):
        return self.node['bbox'][3] - self.node['bbox'][1]

    def get_value(self):
        if 'value' in self.node:
            return self.node['value']
        else:
            return None

    def get_type(self):
        return self.node['type']


class DocumentQueryContext:
    """
    Provides a context around a document that you can use to perform queries
    """

    def __init__(self, document):
        self.document = document
        self.root = self.wrap_content(None, document.content, 0)

    def wrap_content(self, parent, content, index):
        queryable_node = QueryableNode(parent, content, index)
        if content.children:
            idx = 0
            for child in content.children:
                queryable_node.children.append(self.wrap_content(queryable_node, child, idx))
                idx += 1
        return queryable_node
