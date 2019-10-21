import json
from abc import abstractmethod
from typing import TypeVar, Generic, IO

from ._error import JSONSerialiseError
from .._typing import RawJSONElement
from ..validator import JSONValidatorClass

# The type of the serialisable object
T = TypeVar("T", bound="JSONDeserialisable")


class JSONDeserialisable(Generic[T]):
    """
    Interface class for objects which can deserialise themselves from JSON.
    """
    @classmethod
    @abstractmethod
    def _deserialise_from_raw_json(cls, raw_json: RawJSONElement) -> T:
        """
        Implements the actual deserialisation from JSON.

        :param raw_json:    The raw JSON representation.
        :return:            An instance of the type.
        """
        pass

    @classmethod
    def from_raw_json(cls, raw_json: RawJSONElement) -> T:
        """
        Instantiates an object of this type from a raw JSON element.

        :param raw_json:    The raw JSON element.
        :return:            The object instance.
        """
        try:
            # Validate the raw JSON if we are capable
            if issubclass(cls, JSONValidatorClass):
                cls.validate_raw_json(raw_json)

            # Deserialise
            return cls._deserialise_from_raw_json(raw_json)
        except Exception as e:
            raise JSONSerialiseError("Error dumping JSON to string") from e

    @classmethod
    def from_json_string(cls, json_string: str) -> T:
        """
        Instantiates an object of this type from a JSON-format string.

        :param json_string:     The JSON-format string to parse.
        :return:                The object instance.
        """
        try:
            raw_json = json.loads(json_string)
        except Exception as e:
            raise JSONSerialiseError(f"Error parsing JSON string: {json_string}") from e

        return cls.from_raw_json(raw_json)

    @classmethod
    def read_from_stream(cls, stream: IO[str]) -> T:
        """
        Instantiates an object of this type from the given string-stream.

        :param stream:  The stream to read from.
        :return:        The object instance.
        """
        try:
            return cls.from_raw_json(json.load(stream))
        except Exception as e:
            raise JSONSerialiseError("Error reading state from stream") from e

    @classmethod
    def load_from_json_file(cls, filename: str) -> T:
        """
        Loads an instance of this class from the given file.

        :param filename:    The name of the file to load from.
        :return:            The instance.
        """
        try:
            with open(filename, 'r') as file:
                return cls.read_from_stream(file)
        except Exception as e:
            raise JSONSerialiseError(f"Could not load from JSON file '{filename}'") from e
