# pylint: disable=missing-module-docstring
from typing import Any, Callable, Optional, Type, TypeVar

from .objectmapper import ObjectMapper, _InputType, _OutputType
from .exceptions import (ObjectMapperError,
                         DuplicateMappingError,
                         MapTypeError,
                         MapInputKeyError,
                         MapOutputKeyError)


__all__ = ['ObjectMapper',
           'DuplicateMappingError',
           'ObjectMapperError',
           'MapTypeError',
           'MapInputKeyError',
           'MapOutputKeyError',
           'create_map',
           'map']


_OBJECT_MAPPER = ObjectMapper()


def create_map(InputType: Type[_InputType],  # pylint: disable=invalid-name
               OutputType: Type[_OutputType],
               map_function: Callable[[_InputType], _OutputType] = None,
               force: bool = False) \
               -> Optional[Callable[[Callable[[_InputType], _OutputType]], None]]:
    '''Stores a mapping (`map_function`) from objects of type `InputType`
    to an object of type `OutputType`. If `force` is `True`, then any
    pre-existing mapping from `InputType` to `OutputType` is
    overwritten.

    .. testsetup:: create_map_explicit

       import objectmapper

    .. doctest:: create_map_explicit

       >>> objectmapper.create_map(int, str, lambda i: str(i))
       >>> objectmapper.map(42, str)
       '42'

    .. testcleanup:: create_map_explicit

       import importlib
       importlib.reload(objectmapper)

    Can also be used as a _decorator_

    .. testsetup:: create_map_decorator

       import objectmapper

    .. doctest:: create_map_decorator

       >>> @objectmapper.create_map(int, str)
       ... def int_to_str(i: int) -> str:
       ...     return str(i)
       >>> objectmapper.map(42, str)
       '42'

    .. testcleanup:: create_map_decorator

       import importlib
       importlib.reload(objectmapper)

    `MapTypeError` is raised if `InputType` or `OutputType` are not
    types, or if `map_function` is not callable.

    `DuplicateMappingError` is raised if there is a pre-existing
    mapping from `InputType` to `OutputType` and `force` is `False`.
    '''
    return _OBJECT_MAPPER.create_map(InputType, OutputType, map_function, force)


def map(input_instance: Any, OutputType: Type[_OutputType]) -> _OutputType:  # pylint: disable=invalid-name, redefined-builtin
    '''Returns an object of type `OutputType` by giving `input_instance`
    to the mapping from `type(input_instance)` to `OutputType`.

    .. testsetup:: map

       import objectmapper

    .. doctest:: map

       >>> import objectmapper
       >>> @objectmapper.create_map(int, str)
       ... def longform_int_to_str(i: int) -> str:
       ...     digits = (str(x) for x in range(10))
       ...     words = ['zero', 'one', 'two', 'three', 'four',
       ...              'five', 'six', 'seven', 'eight', 'nine']
       ...     digit_to_word = {d: w for d, w in zip(digits, words)}
       ...     return ' '.join(digit_to_word[c] for c in str(i))
       >>> objectmapper.map(451, str)
       'four five one'

    .. testcleanup:: map

       import importlib
       importlib.reload(objectmapper)


    Raises `MapInputKeyError` if there are no mappings from
    `type(input_instance)`.

    Raises `MapOutputKeyError` if there are no mappings from
    `type(input_instance)` to `OutputType`.
    '''
    return _OBJECT_MAPPER.map(input_instance, OutputType)
