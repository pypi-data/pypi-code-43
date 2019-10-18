#!/usr/bin/env python
# -*- coding: utf-8 -*-
import contextlib
from contextlib import contextmanager
from pyraii.close_functor import CloseFunctor
from pyraii.close import close_nothrow, close_multiple


@contextmanager
def closing_on_exception(resource, exception_type=Exception):
    """
    Closes given resource only if a given exception type was thrown while in the context
    By default will close the resource on any exception
    :param resource: needs to adhere to the resource concept
    :param exception_type: will close the resource if the exception which was thrown was of the given type
    :type exception_type: type
    :rtype: contextlib.GeneratorContextManager
    """
    try:
        yield
    except exception_type as e:
        resource.close()
        raise e


@contextmanager
def closing_nothrow(resource):
    """
    Acts similarly to `contextlib.closing` except a failed close is promised to not throw an exception
    :param resource: needs to adhere to the resource concept
    :rtype: contextlib.GeneratorContextManager
    """
    with contextlib.closing(CloseFunctor(on_close=lambda: close_nothrow(resource))):
        yield


@contextmanager
def closing_multiple(resources):
    """
    Will close a collection of resources in a reverse order.
    If fails to close any of the resources, store the thrown exception aside and continue closing the reset of the
    resources and re-raise all intercepted exception inside a `SomeCloseFailedException` exception
    :param resources: sequence of resources
    :rtype: contextlib.GeneratorContextManager
    """
    with contextlib.closing(CloseFunctor(on_close=lambda: close_multiple(resources))):
        yield
