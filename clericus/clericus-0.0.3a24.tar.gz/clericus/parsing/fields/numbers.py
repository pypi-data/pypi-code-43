import math

from .fields import Field, FieldTypes
from ..errors import ParseError

from dataclasses import dataclass, field
from typing import Any, List, Dict


@dataclass
class IntegerField(Field):
    allowedTypes: List = field(default_factory=lambda: [FieldTypes.INTEGER])
    minimum: int = None
    maximum: int = None

    def parser(self, value):
        value = super().parser(value)
        if isinstance(value, str):
            try:
                value = int(value)
            except:
                raise ParseError(message=f"\"{value}\" is not an integer")
        if not isinstance(value, int):
            raise ParseError(message=f"\"{value}\" is not an integer")
        if self.minimum is not None and value < self.minimum:
            raise ParseError(message=f"{value} is less than {self.minimum}")
        if self.maximum is not None and value > self.maximum:
            raise ParseError(message=f"{value} is greater than {self.maximum}")
        return value


@dataclass
class FloatField(Field):
    allowedTypes: List = field(default_factory=lambda: [FieldTypes.FLOAT])
    allowNAN: bool = False
    allowInf: bool = False
    minimum: float = None
    maximum: float = None

    def parser(self, value):
        value = super().parser(value)
        if isinstance(value, str):
            try:
                value = float(value)
            except:
                raise ParseError(message=f"\"{value}\" is not an float")
        if not isinstance(value, float):
            raise ParseError(message=f"\"{value}\" is not an float")
        if not self.allowNAN and math.isnan(value):
            raise ParseError(message="NAN is not allowed")
        if not self.allowNAN and math.isinf(value):
            raise ParseError(message="Infinity is not allowed")
        if self.minimum is not None and value < self.minimum:
            raise ParseError(message=f"{value} is less than {self.minimum}")
        if self.maximum is not None and value > self.maximum:
            raise ParseError(message=f"{value} is greater than {self.maximum}")

        return value