#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created by pat on 3/25/18
"""
.. currentmodule:: events
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Import this module to make event handling a little simpler.
"""

import inspect
from typing import Any, Callable, Iterable, List, NamedTuple, Tuple
import sys
from functools import partial, wraps


class Args(NamedTuple):
    """
    Extend this named tuple to provide easy-to-understand arguments for your events.
    """
    sender: Any  #: the originator of the event


class Event(object):
    """
    An event object wraps a function and notifies a set of handlers when the function is called.
    """
    def __init__(self, f: Callable, sender: Any = None):
        """

        :param f:  the function that triggers the event
        :param sender: the sender of the event
        """
        self._f: Callable = f
        self._handlers: List[Callable] = []
        self._sender = sender

    @property
    def handlers(self) -> Iterable[Callable]:
        """
        Get the handlers for this function.

        :return: an iteration of the handlers.
        """
        return iter(self._handlers)

    def subscribe(self, handler: Callable):
        """
        Subscribe a handler function to this event.

        :param handler: the handler

        .. note::

            You can also use the += operator.
        """
        # Sanity check:  The handler parameter should be a handler function.
        if not isinstance(handler, Callable):
            raise ValueError(f'{type(handler)} is not callable.')
        self._handlers.append(handler)
        return self

    def unsubscribe(self, handler: Callable):
        """
        Unsubscribe a handler function from this event.

        :param handler: the handler

        .. note::

            You can also use the -= operator.
        """
        self._handlers.remove(handler)
        return self

    def __iadd__(self, other):
        # Subscribe to the handler.
        return self.subscribe(other)

    def __isub__(self, other):
        # Unsubscribe from the handler.
        return self.unsubscribe(other)

    def __and__(self, other):
        a = set(self._handlers)
        b = set(other)
        ab = a & b
        self._handlers = [h for h in self._handlers if h in ab]
        return self

    def __or__(self, other):
        a = set(self._handlers)
        b = set(other)
        ab = a | b
        self._handlers = [h for h in self._handlers if h in ab]
        return self

    def trigger(self, *args, **kwargs):
        """
        Trigger the event.
        """
        # Just call all the handlers.
        for h in self._handlers:
            if self._sender is not None:
                h(self._sender, *args, **kwargs)
            else:
                h(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        # The `Event` is callable so that it can be called like a function.
        # When that happens it will first call the function for which it was
        # created...
        self._f(*args, **kwargs)
        # ...then trigger all the handlers.
        self.trigger(*args, **kwargs)


def observable(cls):
    """
    Use this decorator to mark a class that exposes events.

    :param cls: the class
    :return: the class

    .. seealso::

        If you are using this decorator, you probably also want to use :py:func:`event` on
        some of the methods.
    """
    # For starters, we need the class' original __init__ method.
    cls_init = cls.__init__

    @wraps(cls.__init__)
    def init(self, *args, **kwargs):
        # Call the class' original __init__ method.
        cls_init(self, *args, **kwargs)
        # Retrieve all the methods marked as events.
        event_members: List[Tuple[str, Event]] = [
            member for member in inspect.getmembers(self)
            if hasattr(member[1], '__is_event__')
            and member[1].__is_event__
        ]
        for event_member in event_members:
            # Get the attribute name and bound method.
            name_, event_method = event_member
            # If the method we found is a bound method...
            if event_method.__self__ is not None:
                # ...create a new event with a new function that passes this
                # instance in as the first positional (i.e. the "self"
                # parameter).
                setattr(
                    self,
                    name_,
                    Event(
                        f=partial(event_method.__func__.__func__, self),
                        sender=self
                    )
                )
            else:
                # Otherwise, we don't need to supply the 'self' parameter to
                # the function wrapped by the Event object.
                setattr(
                    self,
                    name_,
                    Event(
                        f=event_method.__func__.__func__,
                        sender=cls
                    )
                )
    # Replace the class' original __init__ method with our own.
    cls.__init__ = init
    # The caller gets back the original class.
    return cls


def event(f: Callable) -> Event:
    """
    Decorate a function or method to create an :py:class:`Event`.

    :param f: the function.
    :return: the event

    .. seealso::

        If you are decorating a method within a class, you'll need to use the
        :py:func:`observable` class decorator on the class as well.
    """
    # Create an event object to wrap the function.
    e = Event(f=f)

    @wraps(f)
    def _f(*args, **kwargs):
        e.trigger(*args, **kwargs)
    # Inject some extra doc stuff into the docstring.
    _f.__doc__ = f'⚡ :py:class:`evenz.events.Event`\n{f.__doc__}'
    # Supply the function with some meta information. (This will mostly be used
    # by the @observable decorator.)
    setattr(_f, 'event', e)
    setattr(_f, '__is_event__', True)
    setattr(_f, '__func__', f)

    # If the function is defined directly within a module...
    if f in [_ for _ in inspect.getmembers(f.__module__, inspect.isfunction)]:
        # ...go get the module.
        module_ = sys.modules[f.__module__]
        # Construct some new documentation and append it to the module's
        # documentation.
        doc_parts = [
            module_.__doc__,
            f'⚡ :py:class:`evenz.events.Event` :py:func:`{ f.__name__ }`',
        ]
        doc_parts = filter(lambda p: p is not None, doc_parts)
        module_.__doc__ = '\n'.join(doc_parts)

    # Return the new function.
    return _f


# @observable
# class Dog(object):
#     __test__ = False
#     """
#     This is a sample class that uses events.  It represents a dog that can bark.  Subscribe to
#     the `barked` event to know when it does.
#     """
#
#     def __init__(self, name: str):
#         """
#
#         :param name: the dog's name
#         """
#         self.name = name
#
#     def bark(self, count: int):
#         """
#         Call this method to make the dog bark.
#
#         :param count: How many times will the dog bark?
#         """
#         self.barked(count)
#
#     @event
#     def barked(self, count: int):
#         """
#         This event is raised when the dog barks.
#
#         :param count: how many times did the dog bark?
#         """
