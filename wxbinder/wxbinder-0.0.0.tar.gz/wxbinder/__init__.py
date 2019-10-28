"""Provides the binder, and bind decorators."""


def binder(cls):
    old_init = cls.__init__

    def init(self, *args, **kwargs):
        old_init(self, *args, **kwargs)
        for x in dir(self):
            value = getattr(self, x)
            for event_type in getattr(value, '__event_types__', []):
                self.Bind(event_type, value)

    cls.__init__ = init
    return cls


def bind(*event_types, control=None):
    if not event_types:
        raise RuntimeError('No event types were provided.')

    def inner(func):
        if control is None:
            func.__event_types__ = event_types
        else:
            for event_type in event_types:
                control.Bind(event_type, func)
        return func

    return inner
