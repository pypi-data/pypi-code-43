import math

from .fields import Field, FieldTypes
from ..errors import ParseError

from dataclasses import dataclass, field
from typing import Any, List, Dict


@dataclass
class IntegerField(Field):
    allowedTypes: List = field(default_factory=lambda: [FieldTypes.INTEGER])

    def parser(self, value):
        value = super().parser(value)
        if isinstance(value, str):
            try:
                value = int(value)
            except:
                raise ParseError(
                    message="\"{}\" is not an integer".format(value)
                )
        if not isinstance(value, int):
            raise ParseError(message="\"{}\" is not an integer".format(value))
        return value


@dataclass
class FloatField(Field):
    allowedTypes: List = field(default_factory=lambda: [FieldTypes.FLOAT])
    allowNAN: bool = False
    allowInf: bool = False

    def parser(self, value):
        value = super().parser(value)
        if isinstance(value, str):
            try:
                value = float(value)
            except:
                raise ParseError(
                    message="\"{}\" is not an float".format(value)
                )
        if not isinstance(value, float):
            raise ParseError(message="\"{}\" is not an float".format(value))
        if not self.allowNAN and math.isnan(value):
            raise ParseError(message="NAN is not allowed")
        if not self.allowNAN and math.isinf(value):
            raise ParseError(message="Infinity is not allowed")

        return value