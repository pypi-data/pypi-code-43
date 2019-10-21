from abc import abstractmethod, ABC
from typing import Iterable, Optional, List, Callable, Any, Iterator

from ..._typing import RawJSONElement
from ...serialise import JSONValidatedBiserialisable, JSONSerialisable
from ...schema import JSONSchema, regular_array
from ._Property import Property
from ._DummyInstance import DummyInstance


class ArrayProxy(JSONValidatedBiserialisable['ArrayProxy'], ABC):
    """
    Class which acts like an array, but validates its elements using a property.
    """
    def __init__(self, initial_values: Optional[Iterable] = None):
        # The references to the list elements in the sub-property
        self.__key_list: List[DummyInstance] = []

        # Add any initial values
        if initial_values is not None:
            self.__iadd__(initial_values)

    @classmethod
    @abstractmethod
    def sub_property(cls) -> Property:
        """
        Gets the property which is used to validate elements of the array.
        """
        pass

    @classmethod
    @abstractmethod
    def min_elements(cls) -> int:
        """
        The minimum-allowed length of this array.
        """
        pass

    @classmethod
    @abstractmethod
    def max_elements(cls) -> Optional[int]:
        """
        The maximum-allowed length of this array.
        """
        pass

    @classmethod
    @abstractmethod
    def unique_elements(cls) -> bool:
        """
        Whether the elements of this array have to be distinct
        from one another.
        """
        pass

    def _serialise_to_raw_json(self) -> RawJSONElement:
        return [self.sub_property().get_as_raw_json(key) for key in self.__key_list]

    @classmethod
    def _deserialise_from_raw_json(cls, raw_json: RawJSONElement) -> 'ArrayProxy':
        # Create the instance
        instance = cls()

        # Create an initial key list
        instance.__key_list = [DummyInstance() for _ in range(len(raw_json))]

        # Deserialise and add the elements of the list
        for key, value in zip(instance.__key_list, raw_json):
            cls.sub_property().set_from_raw_json(key, value)

        return instance

    @classmethod
    def get_json_validation_schema(cls) -> JSONSchema:
        return regular_array(
            cls.sub_property().get_json_validation_schema(),
            cls.min_elements(),
            cls.max_elements(),
            cls.unique_elements()
        )

    # ------------ #
    # LIST METHODS #
    # ------------ #

    def append(self, value):
        # Make sure we're not already at max length
        if len(self.__key_list) == self.max_elements():
            raise ValueError(f"Tried to append to list already of maximum size ({self.max_elements()})")

        # Make sure the unique-elements constraint isn't violated
        if self.unique_elements() and value in self:
            raise ValueError(f"Attempted to add non-unique element")

        # Create a new key reference
        key = DummyInstance()

        # Add the value to the sub-property
        self.sub_property().__set__(key, value)

        # Append the key to the key-list
        self.__key_list.append(key)

    def clear(self):
        # Make sure clearing the list wouldn't violate the minimum size
        if self.min_elements() > 0:
            raise RuntimeError(f"Cannot clear array when minimum size "
                               f"({self.min_elements()}) is greater than zero")

        # Clear the key-list
        self.__key_list.clear()

    def copy(self):
        # TODO
        raise NotImplementedError(ArrayProxy.copy.__qualname__)

    def count(self, value) -> int:
        # TODO
        raise NotImplementedError(ArrayProxy.count.__qualname__)

    def extend(self, iterable: Iterable):
        for value in iterable:
            self.append(value)

    def index(self, value, start: int = 0, stop: int = -1) -> int:
        # TODO
        raise NotImplementedError(ArrayProxy.index.__qualname__)

    def insert(self, index: int, value):
        # Make sure we're not already at max length
        if len(self.__key_list) == self.max_elements():
            raise ValueError(f"Tried to insert into list already of maximum size ({self.max_elements()})")

        # Make sure the unique-elements constraint isn't violated
        if self.unique_elements() and value in self:
            raise ValueError(f"Attempted to insert non-unique element")

        # Create a new key reference
        key = DummyInstance()

        # Add the value to the sub-property
        self.sub_property().__set__(key, value)

        # Insert the key into the key-list
        self.__key_list.insert(index, key)

    def pop(self, index: int = -1):
        # Make sure we're not already at min length
        if len(self.__key_list) == self.min_elements():
            raise ValueError(f"Tried to pop from list already of minimum size ({self.min_elements()})")

        # Get the key
        key = self.__key_list.pop(index)

        # Return the value for the key
        return self.sub_property().__get__(key, None)

    def remove(self, value):
        self.pop(self.index(value))

    def reverse(self):
        self.__key_list.reverse()

    def sort(self, *,
             key: Optional[Callable[[Any], Any]] = lambda k: k,
             reverse: bool = False):
        self.__key_list.sort(key=lambda k: key(self.sub_property().__get__(k, None)), reverse=reverse)

    def __add__(self, x: List) -> List:
        return self[:] + x

    def __contains__(self, value) -> bool:
        return any(self.__values_equal(value, self.sub_property().__get__(key, None)) for key in self.__key_list)

    def __delitem__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(ArrayProxy.__delitem__.__qualname__)

    def __eq__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(ArrayProxy.__eq__.__qualname__)

    def __getitem__(self, y):
        if isinstance(y, slice):
            return [self[i] for i in range(*y.indices(len(self)))]
        else:
            return self.sub_property().__get__(self.__key_list.__getitem__(y), None)

    def __ge__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(ArrayProxy.__ge__.__qualname__)

    def __gt__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(ArrayProxy.__gt__.__qualname__)

    def __iadd__(self, x: Iterable):
        for value in x:
            self.append(value)

    def __imul__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(ArrayProxy.__imul__.__qualname__)

    def __iter__(self) -> Iterator:
        return (self.sub_property().__get__(key, None) for key in self.__key_list)

    def __len__(self) -> int:
        return len(self.__key_list)

    def __le__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(ArrayProxy.__le__.__qualname__)

    def __lt__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(ArrayProxy.__lt__.__qualname__)

    def __mul__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(ArrayProxy.__mul__.__qualname__)

    def __ne__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(ArrayProxy.__ne__.__qualname__)

    def __repr__(self):
        return str(element for element in self)

    def __reversed__(self):
        return (self.sub_property().__get__(key, None) for key in reversed(self.__key_list))

    def __rmul__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(ArrayProxy.__rmul__.__qualname__)

    def __setitem__(self, index: int, value):
        # Make sure the unique-elements constraint isn't violated
        if self.unique_elements() and value in self and not self.__values_equal(self[index], value):
            raise ValueError(f"Attempted to set element to non-unique element")

        # Get the key for the item
        key = self.__key_list[index]

        self.sub_property().__set__(key, value)

    def __str__(self):
        return self.to_json_string()

    @staticmethod
    def __values_equal(v1, v2) -> bool:
        """
        Checks if two values are equivalent in JSON.

        :param v1:      The first value to check.
        :param v2:      The second value to check.
        :return:        True if they are equivalent,
                        False if not.
        """
        # Do simple check first
        if v1 == v2:
            return True

        # Compare the JSON representations of the values
        if isinstance(v1, JSONSerialisable) and isinstance(v2, JSONSerialisable):
            return v1.to_raw_json() == v2.to_raw_json()

        return False
