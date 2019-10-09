from enum import Enum
from abc import abstractmethod

class MyDict(dict):

    @staticmethod
    def convertValue(value, acceptedTypes):
        if value is None or acceptedTypes is None or isinstance(value, acceptedTypes):
            return value

        if type(acceptedTypes) == tuple:
            for t in acceptedTypes:
                try:
                    return MyDict.convertValue(value, t)
                except:
                    pass
            raise Exception(f"Cannot convert {value} to {acceptedTypes}")

        if issubclass(acceptedTypes, MyDict):
            assert isinstance(value, dict)
            return acceptedTypes()._from(value)

        try:
            return acceptedTypes(value)
        except:
            raise Exception(f"Cannot convert {value} to {acceptedTypes}")

    def _set(self, key, value, acceptedTypes=None, acceptedItemTypes=None):
        if value is None:
            if key in self:
                del self[key]
        elif acceptedTypes is None:
            self[key] = value
        elif acceptedTypes == list:
            assert isinstance(value, list)
            self[key] = [MyDict.convertValue(v, acceptedItemTypes) for v in value]
        elif issubclass(type(value), Enum):
            self[key] = value.value
        else:
            self[key] = MyDict.convertValue(value, acceptedTypes)
        return self

    __mappedPropeties = None

    @classmethod
    def _getMappedProperties(cls):
        if cls.__mappedPropeties is None:
            # print(f"Build property list for {cls}")
            properties = {}
            for b in cls.__bases__:
                if issubclass(b, MyDict):
                    properties.update(b._getMappedProperties())
            for (pn, pd) in cls.__dict__.items():
                if pd is None or type(pd) != property:
                    continue
                key = pd.__doc__
                if key is None or len(key) == 0:
                    continue
                properties[pn] = pd
            cls.__mappedPropeties = properties
        return cls.__mappedPropeties

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.__mappedPropeties = None

    def _from(self, value):
        assert value is not None
        assert isinstance(value, dict)
        nullKeys = [key for key in self if key not in value]
        for key in nullKeys:
            del self[key]

            # this can be cached for better performance
        for (pn, pd) in self._getMappedProperties().items():
            key = pd.__doc__
            if key not in value:
                continue
            pd.fset(self, value[key])

        return self


def DictProperty(name: str, acceptedTypes: type=None, acceptedItemTypes: type=None) -> property:
    """

    :rtype:
    """
    def getter(self):
        return self.get(name)

    def setter(self, value):
        return self._set(name, value, acceptedTypes, acceptedItemTypes)

    return property(getter, setter, doc=name)

