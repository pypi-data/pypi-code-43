from enum import Enum
import uuid
from typing import Any, Callable

ValueType = Enum('ValueType', 'int float descriptive complex')


class ResourceCategory(Enum):
    '''
    Resource Category to be subclassed depending on the domain

    Enum
    - ValueType: the type of value stored, it can be int, float,
      descriptive, and complex
        - int or float is expected for values between ranges [lim,lim]
        - descriptive is expected for values in a list of possible
          values
        - complex type are a nice way to say that no validity check
          will be performed
    '''

    def __init__(self, uuid: uuid.UUID, valid_range: Any, value_type: Any,
                 value_parser: Callable[[Any], Any] = None) -> None:
        '''
        Initialize each category with its range and type

        Args:
        - uuid: unique identifier to make each enum unique
        - valid_range: constraint regarding the possible values that
          resource can have
        - value_type: which type better represents the value
        - value_parser: callable to return the expected value
          representation
        '''

        self.valid_range = valid_range
        self.value_type = value_type
        assert isinstance(value_type, ValueType), f'got value type {value_type} expected value type {ValueType}'
        self.value_interpreter = value_parser or (lambda value: value)

    def parse(self, value):
        return self.value_interpreter(value)

    def is_valid(self, value):
        '''
        Check if the value is in the correct range accordingly to its ValueType

        Args:
        - value: value to be checked
        '''
        if value is None or self.value_type is ValueType.complex:
            return True

        if self.value_type in (ValueType.int, ValueType.float):
            return self.valid_range[0] <= value <= self.valid_range[1]

        if self.value_type is ValueType.descriptive:
            return value in self.valid_range

        raise RuntimeError(f'Should not reach here: unexpectd ValueType {self.value_type}')
