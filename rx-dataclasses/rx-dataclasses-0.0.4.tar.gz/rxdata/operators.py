
from functools import partial
from typeguard import check_type
from typing import Mapping, Sequence

import rx
from . import attribute

def invoke(invocation=None):
    def _invoke(*, field=None):
        if invocation is None:
            _invocation = field.type
        else:
            _invocation = invocation

        if isinstance(_invocation, str):
            _invocation = attribute.path.fromstring(_invocation).get()

        assert callable(_invocation)

        def __invoke(source):
            def subscribe(observer, scheduler = None):
                def on_next(value):
                    if isinstance(value, _invocation):
                        pass
                    elif isinstance(value, (str, bytes)):
                        value = _invocation(value)
                    elif isinstance(value, Sequence):
                        value = _invocation(*value)
                    elif isinstance(value, Mapping):
                        value = _invocation(**value)
                    else:
                        value = _invocation(value)

                    observer.on_next(value)

                return source.subscribe(
                    on_next,
                    observer.on_error,
                    observer.on_completed,
                    scheduler)
            return rx.create(subscribe)
        return __invoke
    return partial(_invoke)


def typeguard(guard=None, *, using=None):
    if isinstance(using, str):
        _using = attribute.path.fromstring(using).get()

    else:
        _using = using

    if _using is not None:
        assert callable(using)

    def _typeguard(*, field=None):
        if guard is None:
            _type = field.type
        else:
            _type = guard

        if isinstance(_type, str):
            _type = attribute.path.fromstring(_type).get()

        def __typeguard(source):
            def subscribe(observer, scheduler = None):
                def on_next(value):
                    try:
                        check_type(field.name, value, _type)
                    except TypeError as e:
                        if using is None:
                            raise e
                        else:
                            value = using(value)
                    observer.on_next(value)

                return source.subscribe(
                    on_next,
                    observer.on_error,
                    observer.on_completed,
                    scheduler)
            return rx.create(subscribe)
        return __typeguard
    return partial(_typeguard)

def convert(type, using=None):
    if isinstance(type, str):
        _type = attribute.path.fromstring(type).get()
    else:
        _type = type 

    def _convert(*, field=None):
        if using is None:
            _using = field.type
        else:
            _using = using
        def __convert(source):
            def subscribe(observer, scheduler = None):
                def on_next(value):
                    oftype = False
                    try:
                        check_type(field.name, value, _type)
                        oftype = True
                    except TypeError as e:
                        oftype = False

                    if oftype:
                        value = using(value)

                    observer.on_next(value)

                return source.subscribe(
                    on_next,
                    observer.on_error,
                    observer.on_completed,
                    scheduler)
            return rx.create(subscribe)
        return __convert
    return partial(_convert)

__all__ = ('invoke', 'typeguard', 'convert')