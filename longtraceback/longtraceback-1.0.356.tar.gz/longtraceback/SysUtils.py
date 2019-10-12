#!/usr/bin/env python
"""
System Python handling, to allow our environment to be synthesised for tests.
"""

import sys


class SysModuleReplacement(object):
    """
    Replace a named module with another module, in the 'sys.modules' list.

    The replacement of a module allows us to fake the execution of a module as the only
    module loaded, replacing (say) __main__ or others. The object is intended to be used
    as a context handler, within which the module has been replaced.
    """

    def __init__(self, modname, obj):
        self.modname = modname
        self.obj = obj
        self.stack = []

    def __enter__(self):
        self.stack.append(sys.modules[self.modname])
        sys.modules[self.modname] = self.obj
        return self

    def __exit__(self, exc_class, exc, trace):
        sys.modules[self.modname] = self.stack.pop()


class SysArgvReplacement(object):
    """
    Replace the 'sys.argv' array with another to simulate an invocation of module.

    The object is intended to be used as a context handler.
    """

    def __init__(self, argv):
        self.argv = argv
        self.stack = []

    def __enter__(self):
        self.stack.append(sys.argv)
        sys.argv = self.argv[:]
        return self

    def __exit__(self, exc_class, exc, trace):
        sys.argv = self.stack.pop()


class SysPathReplacement(object):
    """
    Replace the 'sys.path' array with another to change the paths we use to search for modules.

    The object is intended to be used as a context handler.
    """

    def __init__(self, at_start=None, replace=None, at_end=None):
        self.at_start = at_start
        self.at_end = at_end
        self.replace = replace
        self.stack = []

    def __enter__(self):
        self.stack.append(sys.path)
        new_path = sys.path[:]

        if self.replace is not None:
            new_path = self.replace

        if self.at_start:
            if isinstance(self.at_start, list):
                new_path = self.at_start[:].extend(new_path)
            else:
                new_path.insert(0, self.at_start)

        if self.at_end:
            if isinstance(self.at_end, list):
                new_path.extend(self.at_end)
            else:
                new_path.append(self.at_end)

        sys.path = new_path
        return self

    def __exit__(self, exc_class, exc, trace):
        sys.path = self.stack.pop()
