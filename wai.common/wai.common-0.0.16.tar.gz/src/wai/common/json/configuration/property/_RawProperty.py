from .._Absent import Absent
from ...schema import JSONSchema
from ..._typing import RawJSONElement
from .._OptionallyPresent import OptionallyPresent
from ._Property import Property


class RawProperty(Property):
    """
    Property which takes raw JSON values. Uses a schema for validation.
    """
    def __init__(self,
                 name: str,
                 schema: JSONSchema,
                 *,
                 optional: bool = False):
        super().__init__(name, optional=optional)

        self.__schema = schema

    def get_as_raw_json(self, instance) -> OptionallyPresent[RawJSONElement]:
        return self.__get__(instance, None)

    def set_from_raw_json(self, instance, value: OptionallyPresent[RawJSONElement]):
        return self.__set__(instance, value)

    def get_json_validation_schema(self) -> JSONSchema:
        return self.__schema

    def validate_value(self, value: RawJSONElement):
        super().validate_value(value)

        # No need to continue validation if value is absent
        if value is Absent:
            return

        # Validate the raw JSON with our schema
        try:
            self.validate_raw_json(value)
        except Exception as e:
            raise AttributeError(f"{value} failed schema validation") from e
