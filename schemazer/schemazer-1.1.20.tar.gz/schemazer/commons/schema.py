from schemazer.base import SchemazerSchema
from schemazer.commons.groups import AuthGroup


class BaseSchema(SchemazerSchema):
    auth = AuthGroup
