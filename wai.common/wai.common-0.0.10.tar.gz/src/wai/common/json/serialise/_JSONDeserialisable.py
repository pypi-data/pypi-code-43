import json
from typing import TypeVar, Generic, IO

from ...meta import has_been_overridden
from ._error import JSONSerialiseError
from .._typing import RawJSONElement
from ..validator import JSONValidatorInstance

# The type of the serialisable object
T = TypeVar("T", bound="JSONDeserialisable")


class JSONDeserialisable(Generic[T]):
    """
    Interface class for objects which can deserialise themselves from JSON. Must override
    one of either from_raw_json or from_json_string.
    """
    def __getattribute__(self, item):
        # Make sure we validate our raw JSON if we are a JSON validator
        if item == JSONDeserialisable.from_raw_json.__name__ and \
                isinstance(self, JSONValidatorInstance):
            return self.with_validation(super().__getattribute__(item))
        else:
            return super().__getattribute__(item)

    @classmethod
    def from_raw_json(cls, raw_json: RawJSONElement) -> T:
        """
        Instantiates an object of this type from a raw JSON element.

        :param raw_json:    The raw JSON element.
        :return:            The object instance.
        """
        try:
            json_string = json.dumps(raw_json)
        except Exception as e:
            raise JSONSerialiseError("Error dumping JSON to string") from e

        return cls.from_json_string(json_string)

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
            if has_been_overridden(JSONDeserialisable.from_raw_json, cls):
                return cls.from_raw_json(json.load(stream))
            else:
                return cls.from_json_string(stream.read())
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
