#!/usr/bin/env python
# -*- coding: utf-8 -*-


def close_nothrow(resource):
    """
    When using this method it is promised that failing to close a given thing will not result in an exception.
    And simply we lead to the "leakage" of the resource
    """
    try:
        resource.close()
    except Exception:
        pass


class SomeCloseFailedException(Exception):
    """
    Indicates some resources were failed to close.
    Holds the failed to close resources and the reason for the failed closing(an Exception)
    """
    def __init__(self, resource_close_failings):
        """
        :type resource_close_failings: list[tuple[object,Exception]]
        """
        self.resource_close_failings = resource_close_failings


def close_multiple(resources):
    """
    Will close an iterable collection of resources in a reverse order.
    If fails to close any of the resources, store the thrown exception aside and continue closing the reset of the
    resources and re-raise all intercepted exception inside a `SomeCloseFailedException` exception

    .. code-block:: python
        close_multiple(resource_1, bad_resource_2, resource_3, bad_resource_4, resource_5)

    In the example after the function is called
    * resource 5 was closed
    * resource 4 failed to closed with `exception_a`
    * resource 3 was closed
    * resource 2 failed to closed with `exception_b`
    * resource 1 was closed
    * `SomeCloseFailedException` was thrown holding `exception_a` and  `exception_b`

    The reason for the reverse order of closing is to imitate the destruction of C++ objects.
    If you initialize a collection of resources it may be possible that the latest resources are dependent on the first
    resources you initialized. To prevent a situation where a closing of resource A will not cause errors for resource B
    which depends on it.

    :param resources: sequence of resources
    """
    resource_close_failings = []

    for resource in reversed(resources):
        try:
            resource.close()
        except Exception as e:
            resource_close_failings.append((resource, e))

    if len(resource_close_failings):
        raise SomeCloseFailedException(resource_close_failings)
