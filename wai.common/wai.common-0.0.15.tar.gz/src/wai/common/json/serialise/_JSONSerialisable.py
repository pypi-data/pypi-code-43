import json
from abc import abstractmethod
from typing import IO

from ._error import JSONSerialiseError
from .._typing import RawJSONElement
from ..validator import JSONValidatorInstance


class JSONSerialisable:
    """
    Interface class for objects which can serialise themselves to JSON.
    """
    @abstractmethod
    def _serialise_to_raw_json(self) -> RawJSONElement:
        """
        Performs the actual serialisation.

        :return:    The JSON representation.
        """
        pass

    def to_raw_json(self) -> RawJSONElement:
        """
        Converts the state of this object to a raw JSON element.

        :return:    The raw JSON.
        """
        try:
            # Get the raw JSON representation
            raw_json: RawJSONElement = self._serialise_to_raw_json()

            # Validate the JSON if we are capable
            if isinstance(self, JSONValidatorInstance):
                self.validate_raw_json(raw_json)

            return raw_json
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
            json.dump(self.to_raw_json(), stream)
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
