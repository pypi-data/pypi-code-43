from functools import wraps

from cathartidae.builder_args import BuilderArgs
from cathartidae.control_decorator import ControlDecorator
from cathartidae.control_decorator_builder import ControlDecoratorBuilder
from cathartidae.lib.echos import echo, dynamic_echo

__all__ = ["build_decorator", "build_decorator_dynamic"]


def build_decorator(abstracted_block_constructor, operand, func, default=None):
    return build_decorator_inner(abstracted_block_constructor, echo, operand, func, default)


def build_decorator_dynamic(abstracted_block_constructor, operand, func, default=None):
    return build_decorator_inner(abstracted_block_constructor, dynamic_echo, operand, func, default)


def build_decorator_inner(abstracted_block_constructor, operand_pre_operation, operand, func, default=None):
    if type(func) is staticmethod or type(func) is classmethod:
        raise ValueError("can not decorate staticmethod/classmethod, make those the outermost decorator")
    builder_args = BuilderArgs(operand, default, func)
    control_decorator_builder = ControlDecoratorBuilder(abstracted_block_constructor, operand_pre_operation)
    try:
        return wraps(func)(ControlDecorator(builder_args, control_decorator_builder))
    except AttributeError:
        raise ValueError("can not decorate provided function, did you make staticmethod/classmethod the outermost decorator")
