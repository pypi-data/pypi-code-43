from data_mapper.properties.abstract import AbstractProperty
from data_mapper.properties.functional.operation import Operation


class BinaryOperation(Operation):
    def __init__(
            self,
            prop1: AbstractProperty,
            prop2: AbstractProperty,
            **kwargs,
    ):
        super().__init__(prop1, prop2, **kwargs)
