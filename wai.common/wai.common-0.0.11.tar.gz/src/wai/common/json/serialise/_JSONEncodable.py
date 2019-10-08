from abc import ABC, abstractmethod
from json import JSONEncoder
from typing import Any

from ._JSONSerialisable import JSONSerialisable
from ._error import JSONSerialiseError


class JSONEncodable(JSONSerialisable, ABC):
    """
    Interface for classes which serialise themselves to JSON using
    a JSON encoder and a custom JSON representation.
    """
    @abstractmethod
    def get_custom_json_encoder(self) -> JSONEncoder:
        """
        Gets the custom JSON encoder to use to encode this object's
        custom JSON representation.

        :return:    The encoder.
        """
        pass

    @abstractmethod
    def to_custom_json(self) -> Any:
        """
        Gets the custom JSON representation of this object
        for use with the JSON encoder. Custom JSON can contain
        other types than just the standard JSON types, so long
        as the corresponding encoder supports them.
        """
        pass

    def to_json_string(self) -> str:
        try:
            return self.get_json_encoder().encode(self.to_custom_json())
        except Exception as e:
            raise JSONSerialiseError(f"Error encoding object using custom encoder") from e
