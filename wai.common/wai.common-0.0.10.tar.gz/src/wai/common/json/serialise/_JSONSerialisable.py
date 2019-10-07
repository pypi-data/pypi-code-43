import json
from typing import IO

from ...meta import has_been_overridden
from ._error import JSONSerialiseError
from .._typing import RawJSONElement
from ..validator import JSONValidatorInstance


class JSONSerialisable:
    """
    Interface class for objects which can serialise themselves to JSON. Must override
    one of either to_raw_json or to_json_string.
    """
    def __getattribute__(self, item):
        # Make sure we validate our raw JSON if we are a JSON validator
        if item == JSONSerialisable.to_raw_json.__name__ and \
                isinstance(self, JSONValidatorInstance):
            return self.with_validation(super().__getattribute__(item))
        else:
            return super().__getattribute__(item)

    def to_raw_json(self) -> RawJSONElement:
        """
        Converts the state of this object to a raw JSON element.

        :return:    The raw JSON.
        """
        try:
            # Get the raw JSON representation
            return json.loads(self.to_json_string())
        except Exception as e:
            raise JSONSerialiseError("Error converting object to raw JSON") from e

    def to_json_string(self) -> str:
        """
        Serialises this object to a JSON-format string.

        :return:    The JSON string.
        """
        try:
            return json.dumps(self.to_raw_json())
        except Exception as e:
            raise JSONSerialiseError("Error converting object to JSON string") from e

    def write_to_stream(self, stream: IO[str]) -> None:
        """
        Writes this object as JSON to a string-stream.

        :param stream:  The stream to write to.
        """
        try:
            if has_been_overridden(JSONSerialisable.to_raw_json, self):
                json.dump(self.to_raw_json(), stream)
            else:
                stream.write(self.to_json_string())
        except Exception as e:
            raise JSONSerialiseError("Error writing state to stream") from e

    def save_to_json_file(self, filename: str) -> None:
        """
        Saves this object to the given file.

        :param filename:    The name of the file to save to.
        """
        try:
            with open(filename, 'w') as file:
                self.write_to_stream(file)
        except Exception as e:
            raise JSONSerialiseError(f"Could not save to JSON file '{filename}'") from e
