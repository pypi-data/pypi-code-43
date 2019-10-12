from schemazer.base import SchemazerResponseField


class FloatField(SchemazerResponseField):
    type = float
    data_example = 123.12


class IntField(SchemazerResponseField):
    type = int
    data_example = 123


class StringField(SchemazerResponseField):
    type = str
    data_example = 'string'


class BooleanField(SchemazerResponseField):
    type = bool
    data_example = True


class ListField(SchemazerResponseField):
    type = list
    data_example = []


class IDField(IntField):
    name = 'id'
    description = 'ID field'
    data_example = '242d40ee-3b64-49dd-abb0-60574f73af7f'


class TokenField(StringField):
    name = 'token'
    description = 'Unique auth token.'
    data_example = '1q2w3e4r5t6y7u8i9o0p1q2w3e4r5t6y7u8i9o0p'


class SuccessField(BooleanField):
    name = 'success'
    description = 'Status operation.'
    data_example = True


class UsernameField(StringField):
    name = 'username'
    description = 'Username'
    data_example = 'User007'


class TimestampField(FloatField):
    name = 'date'
    description = 'Time stamp field'
    data_example = 1554316678.361951
