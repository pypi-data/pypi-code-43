from .validator import JSONValidatorInstance
from .schema import JSONSchema


class BasicSchemaValidator(JSONValidatorInstance):
    """
    Basic wrapper for a JSON schema which presents it as a validator.
    """
    def __init__(self, schema: JSONSchema):
        self.__schema = schema

    def get_json_validation_schema(self) -> JSONSchema:
        return self.__schema
