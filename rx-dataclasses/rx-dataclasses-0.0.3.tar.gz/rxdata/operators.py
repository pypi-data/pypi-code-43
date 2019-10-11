
from functools import partial
from typeguard import check_type
from typing import Mapping, Sequence

import rx
from . import utils

def typeguard(guard=None):
    def _typeguard(*, field=None):
        if guard is None:
            _type = field.type
        else:
            _type = guard

        if isinstance(_type, str):
            _type = utils.imported(*utils.convertpath(_type))

        def __typeguard(source):
            def subscribe(observer, scheduler = None):
                def on_next(value):
                    check_type(field.name, value, _type)
                    observer.on_next(value)

                return source.subscribe(
                    on_next,
                    observer.on_error,
                    observer.on_completed,
                    scheduler)
            return rx.create(subscribe)
        return __typeguard
    return partial(_typeguard)

def invoke(invocation=None):
    def _invoke(*, field=None):
        if invocation is None:
            _invocation = field.type
        else:
            _invocation = invocation

        if isinstance(_invocation, str):
            _invocation = utils.imported(*utils.convertpath(_invocation))

        assert callable(_invocation)

        def __invoke(source):
            def subscribe(observer, scheduler = None):
                def on_next(value):

                    if isinstance(value, (str, bytes)):
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
