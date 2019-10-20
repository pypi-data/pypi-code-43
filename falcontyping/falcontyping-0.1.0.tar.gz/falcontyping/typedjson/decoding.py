"""
The MIT License (MIT)

Copyright (c) 2018 Tomoya Kose

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

This is a modified version of the decoding module at:
https://github.com/mitsuse/typedjson-python/blob/master/typedjson/decoding.py

Author: Tomoya Kose <tomoya@mitsuse.jp>
Repository: https://github.com/mitsuse/typedjson-python
"""
from typing import Any, Iterator, List, Optional, Tuple, Type, TypeVar, Union

try:
    from pydantic import BaseModel as PydanticBaseModel

except ImportError:
    PydanticBaseModel = None  # type: ignore


try:
    from marshmallow import Schema as MarshmallowSchema

except ImportError:
    MarshmallowSchema = None  # type: ignore


Decoded = TypeVar("Decoded")
Value = TypeVar("Value")

Path = Tuple[str, ...]


class TypeMismatch(Exception):
    def __init__(self, path: Path) -> None:
        self.__path = path

    def __eq__(self, x: Any) -> bool:
        if isinstance(x, TypeMismatch):
            return self.path == x.path
        else:
            return False

    def __str__(self) -> str:
        return f"<TypeMismatch path={self.path}>"

    @property
    def path(self) -> Path:
        return self.__path


class UnsupportedDecoding(Exception):
    def __init__(self, path: Path) -> None:
        self.__path = path

    def __eq__(self, x: Any) -> bool:
        if isinstance(x, UnsupportedDecoding):
            return self.path == x.path
        else:
            return False

    def __str__(self) -> str:
        return f"<UnsupportedDecoding path={self.path}>"

    @property
    def path(self) -> Path:
        return self.__path


class ExternalSerializerException(Exception):
    def __init__(self, path: Path, exception: Exception) -> None:
        self.__path = path
        self.exception = exception

    def __eq__(self, x: Any) -> bool:
        if isinstance(x, ExternalSerializerException):
            return self.path == x.path
        else:
            return False

    def __str__(self) -> str:
        return f"<ExternalException path={self.path}>"

    @property
    def path(self) -> Path:
        return self.__path


FailureReason = Union[TypeMismatch, UnsupportedDecoding, ExternalSerializerException]


class DecodingError(Exception):
    def __init__(self, reason: FailureReason) -> None:
        self.__reason = reason

    def __eq__(self, x: Any) -> bool:
        if isinstance(x, DecodingError):
            return self.reason == x.reason
        else:
            return False

    def __str__(self) -> str:
        return f"<DecodingError reason={self.reason}>"

    @property
    def reason(self) -> FailureReason:
        return self.__reason


def serialize_pydantic(type_: Any, json: Any, path: Path) -> Union[Decoded, DecodingError]:
    try:
        return type_(**json)  # type: ignore

    except Exception as e:
        return DecodingError(reason=ExternalSerializerException(path, exception=e))


def serialize_marshmallow(type_: Any, json: Any, path: Path) -> Union[Decoded, DecodingError]:
    try:
        return type_().load(json)  # type: ignore

    except Exception as e:
        return DecodingError(reason=ExternalSerializerException(path, exception=e))


def decode(
    type_: Type[Decoded], json: Any, path: Path = ()
) -> Union[Decoded, DecodingError]:
    decoders = (
        decode_as_union,
        decode_as_tuple,
        decode_as_list,
        decode_as_primitive,
        # decode_as_class,
    )

    result_final: Union[Decoded, DecodingError] = DecodingError(
        UnsupportedDecoding(path)
    )
    for d in decoders:
        result = d(type_, json, path)

        if isinstance(result, DecodingError):
            if isinstance(result.reason, TypeMismatch):
                result_final = result
        else:
            result_final = result
            break

    return result_final


def decode_as_primitive(
    type_: Type[Decoded], json: Any, path: Path
) -> Union[Decoded, DecodingError]:
    from .annotation import origin_of

    if origin_of(type_) is Union:
        return DecodingError(UnsupportedDecoding(path))

    if isinstance(json, type_):
        return json

    elif type_ in (str, float, int, bool, type(None)):
        if type_ is int and isinstance(json, str):
            try:
                number = float(json)

                if number.is_integer():
                    return int(number)  # type: ignore

            except ValueError:
                ...

        return DecodingError(TypeMismatch(path))

    elif PydanticBaseModel and issubclass(type_, PydanticBaseModel):
        if json:
            return serialize_pydantic(type_, json=json, path=path)

        else:
            return DecodingError(TypeMismatch(path))

    elif MarshmallowSchema and issubclass(type_, MarshmallowSchema):
        if json:
            return serialize_marshmallow(type_, json=json, path=path)

        else:
            return DecodingError(TypeMismatch(path))

    else:
        return DecodingError(UnsupportedDecoding(path))


def decode_as_class(
    type_: Type[Decoded], json: Any, path: Path
) -> Union[Decoded, DecodingError]:
    from .annotation import hints_of

    def _decode(annotation: Tuple[str, Any]) -> Union[Decoded, DecodingError]:
        key, type_ = annotation
        value = json.get(key)
        return decode(type_, value, path + (key,))

    annotations = hints_of(type_)
    if isinstance(json, dict) and annotations is not None and type_ is not Any:
        parameters = tuple(map(_decode, annotations.items()))

        for parameter in parameters:
            if isinstance(parameter, DecodingError):
                return parameter

        return type_(*parameters)
    else:
        return DecodingError(UnsupportedDecoding(path))


def decode_as_union(
    type_: Type[Decoded], json: Any, path: Path
) -> Union[Decoded, DecodingError]:
    from .annotation import args_of
    from .annotation import origin_of

    if origin_of(type_) is Union:
        args = args_of(type_)
        for type_ in args:
            if type_.__class__ is TypeVar:
                return DecodingError(UnsupportedDecoding(path))

        for type_ in args:
            decoded = decode(type_, json, path)
            if not isinstance(decoded, DecodingError):
                break

        return decoded
    else:
        return DecodingError(UnsupportedDecoding(path))


def decode_as_tuple(
    type_: Type[Decoded], json: Any, path: Path
) -> Union[Decoded, DecodingError]:
    from .annotation import args_of
    from .annotation import origin_of

    def _required_length(args: Tuple[Type, ...]) -> int:
        return len(args) - 1 if args[-1] is ... else len(args)

    def _iter_args(args: Tuple[Type, ...]) -> Iterator[Type]:
        last: Optional[Type] = None
        for type_ in args:
            if type_ is ...:
                if last is None:
                    raise  # pylint: disable=misplaced-bare-raise
                else:
                    while True:
                        yield last
            else:
                yield type_
            last = type_

    if origin_of(type_) is tuple:
        list_decoded: List[Any] = []
        length = len(json)
        if _required_length(args_of(type_)) > length:
            return DecodingError(TypeMismatch(path))

        for (index, (type_, element)) in enumerate(
            zip(_iter_args(args_of(type_)), json)
        ):
            decoded = decode(type_, element, path + (str(index),))
            if isinstance(decoded, DecodingError):
                return decoded

            list_decoded.append(decoded)

        return tuple(list_decoded)  # type: ignore
    else:
        return DecodingError(UnsupportedDecoding(path))


def decode_as_list(
    type_: Type[Decoded], json: Any, path: Path
) -> Union[Decoded, DecodingError]:
    from .annotation import args_of
    from .annotation import origin_of

    if origin_of(type_) is list:
        Element = args_of(type_)[0]
        list_decoded: List[Any] = []

        for index, element in enumerate(json):
            decoded = decode(Element, element, path + (str(index),))
            if isinstance(decoded, DecodingError):
                return decoded

            list_decoded.append(decoded)

        return list(list_decoded)  # type: ignore
    else:
        return DecodingError(UnsupportedDecoding(path))
