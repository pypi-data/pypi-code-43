import io

from ._JSONSerialisable import JSONSerialisable
from ._JSONDeserialisable import JSONDeserialisable, T
from ._error import JSONSerialiseError


class JSONBiserialisable(JSONSerialisable, JSONDeserialisable[T]):
    """
    Interface for classes which implement both JSONSerialisable and
    JSONDeserialisable[T].
    """
    def json_copy(self) -> T:
        """
        Creates a copy of this object by serialising to JSON and
        then deserialising again.

        :return:    The copy of this object.
        """
        try:
            return self.from_raw_json(self.to_raw_json())
        except Exception as e:
            raise JSONSerialiseError("Error copying object using JSON serialisation") from e
