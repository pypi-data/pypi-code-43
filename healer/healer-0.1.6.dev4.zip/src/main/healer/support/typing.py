"""
Common class traits
"""

from __future__ import annotations

import enum
import functools
import inspect
import logging
import threading
import traceback
from dataclasses import dataclass
from types import FunctionType
from typing import Any
from typing import Callable
from typing import List
from typing import Type

from healer.support.process import make_solo_line

logger = logging.getLogger(__name__)


def unused(*args, **kwargs) -> None:
    "suppress unused warning in i.d.e."


def type_name(instance:object) -> str:
    """
    Object class name
    """
    return type(instance).__name__


def enum_name_list(enum_klaz:Type[enum.Enum]) -> List[str]:
    """
    List of enumeration member names
    """
    return list(enum_klaz.__members__.keys())


def bucket_class_list(bucket_type:Type, base_type:Type) -> List[Type]:
    """
    List of inner classes of given contanier type, derived from a base type
    """
    return [
        entry for entry in bucket_type.__dict__.values()
        if inspect.isclass(entry) and issubclass(entry, base_type)
    ]


class cached_method(object):
    """
    Decorator: class method with result cache
    """

    CACHE = "__cached_method__"

    def __init__(self, function):
        self.function = function
        functools.update_wrapper(self, function)

    def __get__(self, instance, cls=None):
        if instance is None:
            return self.function
        else:
            return functools.partial(self, instance)

    def __call__(self, *args, **kwargs):
        instance = args[0]

        if not hasattr(instance, self.CACHE):
            object.__setattr__(instance, self.CACHE, dict())

        cache = getattr(instance, self.CACHE)

        key = (self.function, frozenset(args[1:]), frozenset(kwargs.items()))

        if not key in cache:
            cache[key] = self.function(*args, **kwargs)

        value = cache[key]

        return value


class cached_property:  # TODO
    "trait: lazy init property from instance method (not class, not static)"

    def __init__(self, function:Callable):
        self.function = function
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__
        self.lock = threading.RLock()

    def __get__(self, instance, instance_type=None):
        print(f"instance: {instance}")
        if instance is None: return None
        self_name = self.__name__
        self_dict = instance.__dict__
        with self.lock:
            if self_name not in self_dict:
                self_dict[self_name] = self.function(instance)
        return self_dict[self_name]


class static_cached_property:  # TODO
    "trait: lazy init property from static method (not class, not instance)"

    def __init__(self, function:Callable):
        self.function = function
        self.__name__ = function.__name__
        self.__doc__ = function.__doc__
        self.lock = threading.RLock()

    def __get__(self, instance, instance_type):
        print(f"@ {self} :: {instance} :: {instance_type}")
        assert instance is None
        self_name = "@" + self.__name__
        self_dict = instance_type.__dict__
        with self.lock:
            if self_name not in self_dict:
                self_dict[self_name] = self.function()
        print(self_dict)
        return self_dict[self_name]


class WithInstanceRegistry:
    """
    Trait: track all class instancess
    """

    instance_object_list:List[object] = []

    def __new__(cls, *args, **kwargs) -> object:
        instance_object = super().__new__(cls)
        cls.instance_register(instance_object)
        return instance_object

    @classmethod
    def instance_register(cls, instance_object:object):
        if not instance_object in cls.instance_object_list:
            cls.instance_object_list.append(instance_object)

    @classmethod
    def instance_unregister(cls, instance_object:object):
        if instance_object in cls.instance_object_list:
            cls.instance_object_list.remove(instance_object)


class WithTypeName:
    """
    Trait: get class name
    """

    def type_name(self) -> str:
        return type_name(self)


class WithLogger:
    """
    Trait: provide logger with class name
    """

    logger:logging.Logger

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.logger = logging.getLogger(self.__class__.__qualname__)


class WithLoggerSTD(WithLogger):
    """
    Trait: provide logger with stdout/stderr channel
    """

    def react_stdout(self, line:str) -> None:
        line = make_solo_line(line)
        self.logger.info(f"[stdout] {line}")

    def react_stderr (self, line:str) -> None:
        line = make_solo_line(line)
        self.logger.info(f"[stderr] {line}")


def discover_class_from_method(method:Callable) -> Type:
    assert inspect.ismethod(method), f"Expecting method: {method}"
    for cls in inspect.getmro(method.__self__.__class__):
        if cls.__dict__.get(method.__name__) is method:
            return cls
    raise RuntimeError(f"Missing class for method: {method}")


class AutoNameEnum(enum.Enum):
    """
    Enum with automatic name generation
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values) -> str:
        return name

    def __repr__(self) -> str:
        return self.name

    def __get__(self, instance, owner) -> str:
        return self.name


def override(method:FunctionType) -> FunctionType:
    "decorator for method override"  # TODO
    return method


def proper_class_name(klas:Type) -> str:
    "extract fqcn: package.module.class"
    module = klas.__module__
    if module is None or module == str.__class__.__module__:
        return klas.__name__
    else:
        return module + '.' + klas.__name__


def proper_class_name_for(instance:object) -> str:
    klas = type(instance)
    return proper_class_name(klas)


class TypingSupport:

    @staticmethod
    def cast_base_to_derived(base_instance:object, derived_type:Type) -> None:
        object.__setattr__(base_instance, '__class__', derived_type)

    @staticmethod
    def object_settattr(instance:object, key:str, value:Any) -> None:
        object.__setattr__(instance, key, value)


def render_error_trace(error:Exception, limit:int=3) -> str:
    "convert stack trace to single line"
    trace_list = traceback.format_exception(
        etype=None, value=error, tb=error.__traceback__, limit=limit,
    )
    trace_line = "".join(trace_list).replace('\n', ' | ')
    return trace_line
