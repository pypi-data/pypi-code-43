from abc import abstractmethod
from json import JSONDecoder
from typing import Any

from ._JSONDeserialisable import JSONDeserialisable, T
from ._error import JSONSerialiseError


class JSONDecodable(JSONDeserialisable[T]):
    """
    Interface for classes which deserialise themselves from JSON using
    a JSON decoder and a custom JSON representation.
    """
    @classmethod
    @abstractmethod
    def get_custom_json_decoder(cls) -> JSONDecoder:
        """
        Gets the custom JSON decoder to use to decode a JSON
        string into the class' custom JSON representation.

        :return:    The decoder.
        """
        pass

    @classmethod
    @abstractmethod
    def from_custom_json(cls, custom_json: Any) -> T:
        """
        Creates an instance of this class from its custom JSON
        representation.
        """
        pass

    @classmethod
    def from_json_string(cls, json_string: str) -> T:
        try:
            return cls.from_custom_json(cls.get_custom_json_decoder().decode(json_string))
        except Exception as e:
            raise JSONSerialiseError(f"Error decoding object using custom decoder") from e
