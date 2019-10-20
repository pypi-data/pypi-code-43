"""Utilities."""
import itertools
import re
from typing import Any, Callable, List, Set, Union, get_type_hints

import falcon

from falcontyping.typedjson import args_of, origin_of

from .exceptions import TypeValidationError

try:
    from typing_extensions import Protocol

    class ResourceMethodWithoutReturnValue(Protocol):

        def __call__(self, request: falcon.Request, respone: falcon.Response, **kwargs: Any) -> None:
            ...

    class ResourceMethodWithReturnValue(Protocol):

        def __call__(self, request: falcon.Request, respone: falcon.Response, **kwargs: Any) -> Any:
            ...

except ImportError:
    ResourceMethodWithoutReturnValue = Callable  # type: ignore
    ResourceMethodWithReturnValue = Callable     # type: ignore

try:
    from pydantic import BaseModel as PydanticBaseModel

except ImportError:
    PydanticBaseModel = None  # type: ignore


try:
    from marshmallow import Schema as MarshmallowSchema

except ImportError:
    MarshmallowSchema = None  # type: ignore


_AVAILABLE_EXTERNAL_SCHEMA_PRODIVERS = set(
    filter(None, [MarshmallowSchema, PydanticBaseModel])
)

# Taken from https://github.com/falconry/falcon/blob/master/falcon/routing/compiled.py#L27
_FIELD_PATTERN = re.compile(
    # NOTE(kgriffs): This disallows the use of the '}' character within
    # an argstr. However, we don't really have a way of escaping
    # curly brackets in URI templates at the moment, so users should
    # see this as a similar restriction and so somewhat unsurprising.
    #
    # We may want to create a contextual parser at some point to
    # work around this problem.
    r'{((?P<fname>[^}:]*)((?P<cname_sep>:(?P<cname>[^}\(]*))(\((?P<argstr>[^}]*)\))?)?)}'
)

_METHOD_NAME: List[str] = [
    'on_%s' % method for method in ('get', 'post', 'put', 'patch', 'delete', 'head', 'options')
]


def validate_type_preconditions(type_: Any) -> None:

    def predicate(type_: Any) -> bool:
        has_supported_parent = any(
            issubclass(type_, parent) for parent in _AVAILABLE_EXTERNAL_SCHEMA_PRODIVERS
        )
        return (has_supported_parent or type_ is None) and type_ is not Any

    error = (f'Resource methods must accept/return either Nothing, '
             f'marshmallow.Schema or pydantic.BaseModel not {type_}')

    try:
        origin, args = origin_of(type_), args_of(type_)

        if origin is Union:
            if not all(map(predicate, args)):
                raise TypeValidationError(error)

        elif not predicate(origin or type_):
            raise TypeValidationError(error)

    except TypeError:
        raise TypeValidationError(error)


def validate_method_signature(function: ResourceMethodWithReturnValue, uri_parameters: Set[str]) -> None:
    """Validate whether resource method has the right signature."""
    hints = get_type_hints(function)

    for parameter in uri_parameters:
        if parameter not in hints or hints[parameter] is Any:
            raise TypeValidationError(f'URI parameter {parameter} has no type hint or is not part of method signature')

    validate_type_preconditions(
        hints.pop('return')
    )

    if len(hints) < 2:
        raise TypeValidationError('Every resource method must have the first two parameters as '
                                  'falcon.Request and falcon.Response')

    request, response = itertools.islice(hints.keys(), 2)
    body_parameters = set(hints) - (uri_parameters | set([request, response]))

    if len(body_parameters) > 1:
        raise TypeValidationError('Any resource method can not accept more than one '
                                  'marshmallow.Schema or pydantic.BaseModel as a body parameter')

    for parameter_name in body_parameters:
        validate_type_preconditions(hints[parameter_name])


def patch_resource_methods(uri_template: str, resource: Any) -> None:

    uri_parameters = set(match.group('fname') for match in _FIELD_PATTERN.finditer(uri_template))

    def resource_method_wrapper(function: ResourceMethodWithReturnValue) -> ResourceMethodWithoutReturnValue:
        """
        Wraps resource methods.

        This function will takes whatever is returned by resource methods and assigns
        it to response.media.
        """
        def curried(request: falcon.Request, response: falcon.Response, **kwargs: Any) -> None:
            response.media = function(request, response, **kwargs)

        return curried  # type: ignore

    method_name: str
    for method_name in filter(lambda n: getattr(resource, n, None), _METHOD_NAME):
        method: ResourceMethodWithReturnValue = getattr(resource, method_name)

        try:
            validate_method_signature(method, uri_parameters=uri_parameters)

        except TypeValidationError as e:
            raise TypeValidationError(f'{resource}.{method} raised: {e}') from None

        wrapped = resource_method_wrapper(method)
        wrapped.__doc__ = method.__doc__
        wrapped.__annotations__ = method.__annotations__

        setattr(resource, method_name, wrapped)
