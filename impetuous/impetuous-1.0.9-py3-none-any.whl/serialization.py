""" Serialization to load interaction constructs from YAML
"""
import logging
import re
from uuid import UUID

import dateutil.parser
import yaml

from impetuous.interaction import (Comparison, Conjunction, DeleteRequest,
                                   Field, FindRequest, Gather, InsertRequest,
                                   Param, UpdateRequest)

logger = logging.getLogger(__name__)


def deserialize_request(thing):
    return yaml.load(thing, Loader=APIYamlLoader)


def load_FindRequest(loader, node):
    return FindRequest(**loader.construct_mapping(node, deep=True))

def load_InsertRequest(loader, node):
    return InsertRequest(**loader.construct_mapping(node, deep=True))

def load_UpdateRequest(loader, node):
    return UpdateRequest(**loader.construct_mapping(node, deep=True))

def load_DeleteRequest(loader, node):
    return DeleteRequest(**loader.construct_mapping(node, deep=True))

def load_Gather(loader, node):
    return Gather(**loader.construct_mapping(node, deep=True))

def load_Comparison(loader, node):
    return Comparison(*loader.construct_sequence(node, deep=True))

def load_Conjunction_And(loader, node):
    parts = loader.construct_sequence(node, deep=True)
    return Conjunction.and_(parts=parts)

def load_Conjunction_Or(loader, node):
    parts = loader.construct_sequence(node, deep=True)
    return Conjunction.or_(parts=parts)

def load_Param(loader, node):
    return Param(loader.construct_scalar(node))

def load_Field(loader, node):
    return Field(**loader.construct_mapping(node, deep=True))

def load_datetime(loader, node):
    return dateutil.parser.parse(node.value)

def load_UUID(loader, node):
    return UUID(loader.construct_scalar(node))

class APIYamlLoader(yaml.SafeLoader):
    pass

APIYamlLoader.add_constructor('!im/find', load_FindRequest)
APIYamlLoader.add_constructor('!im/insert', load_InsertRequest)
APIYamlLoader.add_constructor('!im/update', load_UpdateRequest)
APIYamlLoader.add_constructor('!im/delete', load_DeleteRequest)
APIYamlLoader.add_constructor('!im/gather', load_Gather)
APIYamlLoader.add_constructor('!im/param', load_Param)
APIYamlLoader.add_constructor('!im/field', load_Field)
APIYamlLoader.add_constructor('!im/and', load_Conjunction_And)
APIYamlLoader.add_constructor('!im/or', load_Conjunction_Or)
APIYamlLoader.add_constructor('!im/cmp', load_Comparison)
APIYamlLoader.add_constructor('tag:yaml.org,2002:timestamp', load_datetime)
APIYamlLoader.add_constructor('!uuid', load_UUID)
UUID_PATTERN = re.compile(r'\d{8}-\d{4}-\d{4}-\d{4}-\d{12}')
APIYamlLoader.add_implicit_resolver('!uuid', UUID_PATTERN, None)
