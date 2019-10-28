# encoding:utf-8

from ctypes import *


class BaseField(Structure):
    def _to_bytes(self, value):
        if isinstance(value, bytes):
            return value
        else:
            return bytes(str(value), encoding="utf-8")

    def to_dict_raw(self):
        results = {}
        for key, _ in self._fields_:
            _value = getattr(self, key)
            results[key] = _value
        return results

    def to_dict(self):
        results = {}
        for key, _ in self._fields_:
            _value = getattr(self, key)
            if isinstance(_value, bytes):
                results[key] = _value.decode(encoding="gb18030", errors="ignore")
            else:
                results[key] = _value
        return results

    def to_list(self):
        results = []
        for key, _ in self._fields_:
            _value = getattr(self, key)
            if isinstance(_value, bytes):
                results.append(_value.decode(encoding="gb18030", errors="ignore"))
            else:
                results.append(_value)
        return results

    def __repr__(self):
        return f"{self.__class__.__name__}->{self.to_dict()}"

    @classmethod
    def from_dict(cls, obj):
        return cls(**obj)
