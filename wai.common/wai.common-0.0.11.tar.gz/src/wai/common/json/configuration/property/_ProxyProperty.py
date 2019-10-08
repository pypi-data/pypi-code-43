from abc import ABC
from typing import Type

from ..._typing import RawJSONElement
from .._OptionallyPresent import OptionallyPresent
from .._Absent import Absent
from ...schema import JSONSchema
from ...serialise import JSONValidatedBiserialisable
from ._Property import Property


class ProxyProperty(Property, ABC):
    """
    Property which takes values of a type that is serialisable
    to/from JSON.
    """
    def __init__(self,
                 name: str,
                 type: Type[JSONValidatedBiserialisable],
                 *,
                 optional: bool = False):
        super().__init__(
            name,
            optional=optional
        )

        self.__type: Type[JSONValidatedBiserialisable] = type

    def type(self) -> Type[JSONValidatedBiserialisable]:
        """
        Gets the type of this proxy-property.
        """
        return self.__type

    def get_as_raw_json(self, instance) -> OptionallyPresent[RawJSONElement]:
        # Get the proxy value
        value = self.__get__(instance, None)

        # If not absent, serialise it
        return value.to_raw_json() if isinstance(value, JSONValidatedBiserialisable) else value

    def set_from_raw_json(self, instance, value: OptionallyPresent[RawJSONElement]):
        # Deserialise the value
        self.__set__(instance, self.__type.from_raw_json(value) if value is not Absent else Absent)

    def get_json_validation_schema(self) -> JSONSchema:
        return self.__type.get_json_validation_schema()

    def validate_value(self, value):
        super().validate_value(value)

        # No need to continue validation if value is absent
        if value is Absent:
            return

        # Must be an instance of the correct type
        if not isinstance(value, self.__type):
            raise AttributeError(f"{value} is not an instance of {self.__type.__name__}")
