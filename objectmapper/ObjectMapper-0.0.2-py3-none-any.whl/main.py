'''This module implements the API'''

from typing import Any, Callable, Type, TypeVar


_InputType = TypeVar('_InputType')
_OutputType = TypeVar('_OutputType')


class ObjectMapperError(Exception):
    '''Parent exception class'''


class DuplicateMappingError(ObjectMapperError):
    '''Raised when a mapping between classes is redundantly defined without forcing an overwrite.'''
    def __init__(self, InputType, OutputType, mapping):
        super().__init__(f'Mapping already exists from {InputType} to {OutputType} -- {mapping}')


class MapTypeError(ObjectMapperError, TypeError):
    '''Raised when making a mapping between non-types, or map function is non-callable.'''


class MapInputKeyError(ObjectMapperError, KeyError):
    '''Raised when mapping an object of an unknown type.'''
    def __init__(self, InputType):
        super().__init__(f'No mappings found for instances of type {InputType}')


class MapOutputKeyError(ObjectMapperError, KeyError):
    '''Raised when mapping an object to an unknown type.'''
    def __init__(self, InputType, OutputType):
        super().__init__(f'No mappings found from instances of type {InputType} to type'
                         f' {OutputType}')


class ObjectMapper:
    '''Class for recording and accessing mappings between object
    types. This will often be a singleton in user code.

    '''
    def __init__(self) -> None:
        self._mappings = dict()

    def create_map(self,  # pylint: disable=invalid-name
                   InputType: Type[_InputType],
                   OutputType: Type[_OutputType],
                   map_function: Callable[[_InputType], _OutputType],
                   force: bool = False) -> None:
        '''Stores a mapping (`map_function`) from objects of type `InputType`
        to an object of type `OutputType`. If `force` is `True, then
        any pre-existing mapping from `InputType` to `OutputType` is
        overwritten.

        `MapTypeError` is raised if `InputType` or `OutputType` are
        not types, or if `map_function` is not callable.

        `DuplicateMappingError` is raised if there is a pre-existing
        mapping from `InputType` to `OutputType` and `force` is
        `False`.
        '''
        if not all(map(lambda x: isinstance(x, type), [InputType, OutputType])):
            raise MapTypeError(f'Mappings must be between types, not between {type(InputType)} and'
                               f' {type(OutputType)}')
        if not callable(map_function):
            raise MapTypeError(f'Map value must be callable, not {type(map_function)}')

        self._mappings.setdefault(InputType, dict())
        if not force:
            mapping = self._mappings[InputType].get(OutputType, None)
            if mapping:
                raise DuplicateMappingError(InputType, OutputType, mapping)

        self._mappings[InputType][OutputType] = map_function

    def map(self, input_instance: Any, OutputType: Type[_OutputType]) -> _OutputType:  # pylint: disable=invalid-name
        '''Returns an object of type `OutputType` by giving `input_instance`
        to the mapping from `type(input_instance)` to `OutputType`.

        Raises `MapInputKeyError` if there are no mappings from
        `type(input_instance)`.

        Raises `MapOutputKeyError` if there are no mappings from
        `type(input_instance)` to `OutputType`.
        '''
        InputType = type(input_instance)  # pylint: disable=invalid-name
        if InputType not in self._mappings:
            raise MapInputKeyError(InputType)

        map_function = self._mappings[InputType].get(OutputType, None)
        if not map_function:
            raise MapOutputKeyError(InputType, OutputType)

        return map_function(input_instance)
