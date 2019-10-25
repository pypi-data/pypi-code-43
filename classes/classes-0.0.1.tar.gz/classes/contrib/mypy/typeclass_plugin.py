# -*- coding: utf-8 -*-

"""
Custom mypy plugin to solve the temporary problem with untyped decorators.

This problem appears when we try to change the return type of the function.
However, currently it is impossible due to this bug:
https://github.com/python/mypy/issues/3157

This plugin is a temporary solution to the problem.
It should be later replaced with the official way of doing things.

``mypy`` API docs are here:
https://mypy.readthedocs.io/en/latest/extending_mypy.html

We use ``pytest-mypy-plugins`` to test that it works correctly, see:
https://github.com/mkurnikov/pytest-mypy-plugins
"""

from typing import Callable, Optional, Type

from mypy.plugin import FunctionContext, Plugin
from mypy.types import CallableType, UnionType, Instance, TypeOfAny, AnyType

#: Set of full names of our decorators.
_TYPED_DECORATORS = frozenset((
    'ex.TypeClassMethod',
))


def _change_decorator_function_type(
    decorator: CallableType,
    arg_type: CallableType,
) -> CallableType:
    """Replaces revealed argument types by mypy with types from decorated."""
    return decorator.copy_modified(
        arg_types=arg_type.arg_types,
        arg_kinds=arg_type.arg_kinds,
        arg_names=arg_type.arg_names,
        variables=arg_type.variables,
        is_ellipsis_args=arg_type.is_ellipsis_args,
    )


def _update_typeclass_instance(plugin: Plugin):
    """Tells us what to do when one of the typed decorators is called."""
    def decorator(ctx):
        print('_update_typeclass_instance', ctx)
        print()
        if not ctx.args or not ctx.args[0]:
            return ctx.default_signature

        extra_type = plugin.lookup_fully_qualified(ctx.args[0][0].fullname)
        if not extra_type:
            return ctx.default_signature

        if isinstance(ctx.type.args[0], AnyType):
            # It means that function was defined without annotation
            # or with explicit `Any`, we prevent our Union from polution.
            # Because `Union[Any, int]` is just `Any`.
            union_contents = [Instance(extra_type.node, [])]
        else:
            union_contents = [
                Instance(extra_type.node, []),
                ctx.type.args[0],
            ]
        ctx.type.args[0] = UnionType(union_contents)
        return ctx.default_signature
    return decorator


def _adjust_arguments(plugin: Plugin):
    def decorator(ctx):
        print('_adjust_arguments', ctx)

        typeclass_def = ctx.default_return_type.args[2]
        print(typeclass_def, type(typeclass_def))
        ctx.default_return_type.args = [
            typeclass_def.arg_types[0],
            typeclass_def.ret_type,
        ]

        # TODO: use `typeclass_def.arg_types[0] = T`
        typeclass_def.arg_types[0] = AnyType(TypeOfAny.unannotated)
        ctx.default_return_type.args.append(typeclass_def)

        print(ctx.default_return_type, type(ctx.default_return_type))
        print()
        return ctx.default_return_type
    return decorator


def _update_call_signature(plugin: Plugin):
    def decorator(ctx):
        print('_update_call', ctx)
        print(ctx.default_signature, type(ctx.default_signature))

        real_signature = ctx.type.args[2]
        real_signature.arg_types[0] = ctx.type.args[0]
        print(real_signature)

        print()
        return real_signature
    return decorator


class _TypedDecoratorPlugin(Plugin):
    def get_method_signature_hook(self, fullname: str):
        if fullname == 'ex.TypeClassMethod.__call__':
            return _update_call_signature(self)
        if fullname == 'ex.TypeClassMethod.instance':
            return _update_typeclass_instance(self)
        return None

    def get_function_hook(self, fullname: str):
        if fullname == 'ex.typeclass':
            return _adjust_arguments(self)
        return None


def plugin(version: str) -> Type[Plugin]:
    """Plugin's public API and entrypoint."""
    return _TypedDecoratorPlugin
