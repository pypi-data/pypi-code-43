from abc import abstractmethod, ABC
from typing import Iterable, Optional, Dict, Union, Mapping

from ..._typing import RawJSONElement
from ...serialise import JSONValidatedBiserialisable
from ...schema import JSONSchema, standard_object
from ._Property import Property
from ._DummyInstance import DummyInstance


class MapProxy(JSONValidatedBiserialisable['ArrayProxy'], ABC):
    """
    Class which acts like a map, but validates its elements using a property.
    """
    def __init__(self, initial_values: Optional[Union[Iterable, Mapping]] = None, **kwargs):
        # The references to the list elements in the sub-property
        self.__key_map: Dict[str, DummyInstance] = {}

        # Add any initial values
        self.update(initial_values, **kwargs)

    @classmethod
    @abstractmethod
    def sub_property(cls) -> Property:
        """
        Gets the property which is used to validate elements of the map.
        """
        pass

    def _serialise_to_raw_json(self) -> RawJSONElement:
        return {name: self.sub_property().get_as_raw_json(key) for name, key in self.__key_map.items()}

    @classmethod
    def _deserialise_from_raw_json(cls, raw_json: RawJSONElement) -> 'MapProxy':
        # Create the instance
        instance = cls()

        # Deserialise each value
        for name, value in raw_json.items():
            # Create a dummy key
            key = DummyInstance()

            # Add it to the list
            instance.__key_map[name] = key

            # Add the value to the property
            cls.sub_property().set_from_raw_json(key, value)

        return instance

    @classmethod
    def get_json_validation_schema(cls) -> JSONSchema:
        return standard_object(additional_properties=cls.sub_property().get_json_validation_schema())

    # ------------ #
    # DICT METHODS #
    # ------------ #

    def clear(self):
        self.__key_map.clear()

    def copy(self):
        # TODO
        raise NotImplementedError(MapProxy.copy.__qualname__)

    @staticmethod
    def fromkeys(seq, value):
        # TODO
        raise NotImplementedError(MapProxy.fromkeys.__qualname__)

    def get(self, k: str, default=None):
        if k not in self.__key_map:
            return default

        return self[k]

    def items(self):
        return ((key, self[key]) for key in self.keys())

    def keys(self):
        return self.__key_map.keys()

    def pop(self, k, d=None):
        if k not in self:
            if d is None:
                raise KeyError()
            else:
                return d

        value = self[k]
        self.__key_map.pop(k)
        return value

    def popitem(self):
        key, instance = self.__key_map.popitem()

        return key, self.sub_property().__get__(instance, None)

    def setdefault(self, key, default):
        if key not in self:
            self[key] = default

        return self[key]

    def update(self, E=None, **F):
        if E is not None:
            if hasattr(E, "keys") and callable(E.keys):
                for k in E:
                    self[k] = E[k]
            else:
                for k, v in E:
                    self[k] = v

        for k in F:
            self[k] = F[k]

    def values(self):
        return (self[k] for k in self.keys())

    def __contains__(self, key: str) -> bool:
        return key in self.__key_map

    def __delitem__(self, key: str):
        del(self.__key_map[key])

    def __eq__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(MapProxy.__eq__.__qualname__)

    def __getitem__(self, y):
        return self.sub_property().__get__(self.__key_map[y], None)

    def __ge__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(MapProxy.__ge__.__qualname__)

    def __gt__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(MapProxy.__gt__.__qualname__)

    def __iter__(self):
        return iter(self.__key_map)

    def __len__(self):
        return len(self.__key_map)

    def __le__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(MapProxy.__le__.__qualname__)

    def __lt__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(MapProxy.__lt__.__qualname__)

    def __ne__(self, *args, **kwargs):
        # TODO
        raise NotImplementedError(MapProxy.__ne__.__qualname__)

    def __repr__(self):
        return str(dict(self.items()))

    def __setitem__(self, key: str, value):
        # Create a dummy reference
        instance = DummyInstance()

        # Set the value on the sub-property
        self.sub_property().__set__(instance, value)

        # Put the reference in the key-map
        self.__key_map[key] = instance

    def __str__(self):
        return self.to_json_string()
