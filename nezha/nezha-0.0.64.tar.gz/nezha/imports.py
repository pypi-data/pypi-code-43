"""
Although pycharm hinted syntax error, but it works.
I do not know the season.
"""
from __future__ import absolute_import, unicode_literals

import importlib
import sys
from typing import Dict, Any, Optional, Callable

from kombu.five import reraise, string_t


def symbol_by_name(name: str,
                   aliases: Optional[Dict] = None,
                   imp: Optional[object] = None,
                   package: Optional[str] = None,
                   sep: str = '.',
                   default: Any = None,
                   **kwargs: Any) -> Callable:
    """Get symbol by qualified name.

    The name should be the full dot-separated path to the class::

        modulename.ClassName

    Example::

        celery.concurrency.processes.TaskPool
                                    ^- class name

    or using ':' to separate module and symbol::

        celery.concurrency.processes:TaskPool

    If `aliases` is provided, a dict containing short name/long name
    mappings, the name is looked up in the aliases first.

    Examples:
        >>> symbol_by_name('celery.concurrency.processes.TaskPool')
        <class 'celery.concurrency.processes.TaskPool'>

        >>> symbol_by_name('default', {
        ...     'default': 'celery.concurrency.processes.TaskPool'})
        <class 'celery.concurrency.processes.TaskPool'>

        # Does not try to look up non-string names.
        >>> from celery.concurrency.processes import TaskPool
        >>> symbol_by_name(TaskPool) is TaskPool
        True
    """
    aliases = {} if not aliases else aliases
    if imp is None:
        imp = importlib.import_module

    if not isinstance(name, string_t):
        return name  # type: ignore # already a class

    name = aliases.get(name) or name
    sep = ':' if ':' in name else sep
    module_name, _, cls_name = name.rpartition(sep)
    if not module_name:
        cls_name, module_name = None, package if package else cls_name # type: ignore
    try:
        try:
            module = imp(module_name, package=package, **kwargs) # type: ignore
        except ValueError as exc:
            reraise(ValueError,
                    ValueError("Couldn't import {0!r}: {1}".format(name, exc)),
                    sys.exc_info()[2])
        return getattr(module, cls_name) if cls_name else module
    except (ImportError, AttributeError):
        if default is None:
            raise
    return default


if __name__ == '__main__':
    symbol_by_name('utils.idcard.A')()
