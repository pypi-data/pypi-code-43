from schemazer.base import SchemazerLimit


class AllLimit(SchemazerLimit):
    role = 'all'


class AdminLimit(SchemazerLimit):
    role = 'admin'


class ModerLimit(SchemazerLimit):
    role = 'moder'


class UserLimit(SchemazerLimit):
    role = 'user'
