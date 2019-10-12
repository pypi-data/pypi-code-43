#!/usr/bin/env python
"""
Context handler to replace the sys.excepthook with alternatives.

The context handler can be replaced with custom functions to handle the
behaviour of the exceptions generated at the command line prompt.
The intention is to make the display of the exceptions more friendly,
where possible, or to provide a different style of output where that
may help.

The only handler provided at present is that of output to stdout,
rather than stderr. This ensures that all the output from the console
is sent to the same place.

Usage::

    with StdoutDisplayHook():
        <do something that triggers the hooks>
"""

import sys


class ExceptHook(object):

    def __init__(self, callback=None, write=None, formatter=None):
        """
        Create a way to display exceptions.

        @param callback:    Callback function called when exception found
                            (might be used to record recent exceptions)
        @param write:       Function to write the output to the display
                            (to override the default object method)
        @param formatter:   Function to return a list of lines to output
                            (to override the default object method)
        """
        self.callback = callback
        self.last_value = None
        self.enabled = True
        self.__entered = False
        if formatter is not None or \
           getattr(self, 'formatter', None) is None:
            self.formatter = formatter or self.default_formatter

        self.__old_excepthook = None
        if write is not None or \
           getattr(self, 'write', None) is None:
            self.write = write or self.default_write

    def __enter__(self):
        if self.__entered:
            raise TypeError("%s has already been entered" % (self.__class__.__name__,))
        self.__entered = True

        self.__old_excepthook = sys.excepthook
        sys.excepthook = self.excepthook
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not self.__entered:
            raise TypeError("%s cannot be left before it has been entered" % (self.__class__.__name__,))
        self.__entered = False
        self.last_value = None

        sys.excepthook = self.__old_excepthook
        self.__old_excepthook = None

    def excepthook(self, type, value, traceback):  ## pylint: disable=redefined-builtin
        if not self.enabled:
            return self.__old_excepthook(type, value, traceback)

        self.last_value = (type, value, traceback)
        if self.callback:
            self.callback(type, value, traceback)

        result = self.formatter(type, value, traceback)
        for output in result:
            self.write(output)

    @staticmethod
    def default_formatter(exc_type, exc_value, exc_traceback):
        import traceback
        return traceback.format_exception(exc_type, exc_value, exc_traceback)

    @staticmethod
    def default_write(output):
        sys.stderr.write(output)


class StdoutExceptHook(ExceptHook):
    """
    Force exceptions to go to stdout whilst in force.
    """

    @staticmethod
    def write(msg):  ## pylint: disable=method-hidden
        sys.stdout.write(msg)
