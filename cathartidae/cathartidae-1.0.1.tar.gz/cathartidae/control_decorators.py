from cathartidae.abstract_block import *
from cathartidae.lib.build_decorators import build_decorator, build_decorator_dynamic
from cathartidae.lib.decorator_conversion import convert_to_decorator

__all__ = ["if_", "dynamic_if", "with_", "dynamic_with", "dynamic_while",
           "dynamic_while_generator", "for_x_times", "for_x_times_generator", "dynamic_for_x_times",
           "dynamic_for_x_times_generator"]


def if_(condition, default=None):
    return convert_to_decorator(build_decorator, IfBlock, condition, default)


def dynamic_if(dynamic_condition, default=None):
    return convert_to_decorator(build_decorator_dynamic, IfBlock, dynamic_condition, default)


def with_(obj_with_context):
    return convert_to_decorator(build_decorator, WithBlock, obj_with_context)


def dynamic_with(dynamic_obj_with_context):
    return convert_to_decorator(build_decorator_dynamic, WithBlock, dynamic_obj_with_context)


#def while_(condition):
#    return convert_to_decorator(build_decorator, WhileBlock, condition)


#def while_generator(condition):
#    return convert_to_decorator(build_decorator, WhileBlockGenerator, condition)


def dynamic_while(dynamic_condition):
    return convert_to_decorator(build_decorator_dynamic, WhileBlock, dynamic_condition)


def dynamic_while_generator(dynamic_condition):
    return convert_to_decorator(build_decorator_dynamic, WhileBlockGenerator, dynamic_condition)


def for_x_times(x):
    return convert_to_decorator(build_decorator, ForBlock, range(x))


def for_x_times_generator(x):
    return convert_to_decorator(build_decorator, ForBlockGenerator, range(x))


def dynamic_for_x_times(dynamic_x):
    return convert_to_decorator(build_decorator_dynamic, ForBlock, dynamic_x)


def dynamic_for_x_times_generator(dynamic_x):
    return convert_to_decorator(build_decorator_dynamic, ForBlockGenerator, dynamic_x)
