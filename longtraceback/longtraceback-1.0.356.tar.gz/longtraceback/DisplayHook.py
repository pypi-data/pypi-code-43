#!/usr/bin/env python
"""
Context handler to replace the sys.displayhook with alternatives.

The context handler can be replaced with custom functions to handle the
behaviour of the display of results within the command line prompt.
The intention is to make the display of the value outputs much simpler to
read, or more specific to a given use case.

The pretty printing version of the display hook is the main one we supply
here, in addition to the base context handler.

Usage::

    with PPDisplayHook():
        <do something that triggers the hooks>
"""

import sys

try:
    import __builtin__ as builtins  # pylint: disable=import-error
except ImportError:
    # Python 3 only uses the builtins
    import builtins  # pylint: disable=import-error


class DisplayHook(object):

    def __init__(self, callback=None, write=None, formatter=None):
        """
        Create a way to display the results of an evaluation.

        @param callback:    Callback function called with every value received
                            (might be used to record recent values)
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
        self.__old_displayhook = None
        if write is not None or \
           getattr(self, 'write', None) is None:
            self.write = write or self.default_write

    def __enter__(self):
        if self.__entered:
            raise TypeError("%s has already been entered" % (self.__class__.__name__,))
        self.__entered = True

        self.__old_displayhook = sys.displayhook
        sys.displayhook = self.displayhook
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if not self.__entered:
            raise TypeError("%s cannot be left before it has been entered" % (self.__class__.__name__,))
        self.__entered = False
        self.last_value = None

        sys.displayhook = self.__old_displayhook
        self.__old_displayhook = None

    def displayhook(self, value):
        if not self.enabled:
            return self.__old_displayhook(value)

        builtins._ = None
        self.last_value = value
        if self.callback:
            self.callback(value)

        result = self.formatter(value)
        for output in result:
            self.write(output)
            self.write("\n")
        builtins._ = value

    @staticmethod
    def default_formatter(value):
        return (repr(value),)

    @staticmethod
    def default_write(text):
        # Taken from pseudo code example in Python 3.6 documentation.
        try:
            sys.stdout.write(text)
        except UnicodeEncodeError:
            as_bytes = text.encode(sys.stdout.encoding, 'backslashreplace')
            if hasattr(sys.stdout, 'buffer'):
                sys.stdout.buffer.write(as_bytes)  # pylint: disable=no-member
            else:
                text = as_bytes.decode(sys.stdout.encoding, 'strict')
                sys.stdout.write(text)


class PPDisplayHook(DisplayHook):
    """
    Pretty Printing version of the display hook.
    """
    def __init__(self, *args, **kwargs):
        import pprint
        self.pformat = pprint.pformat
        super(PPDisplayHook, self).__init__(*args, **kwargs)

    def formatter(self, value):  # pylint: disable=method-hidden
        if value is None:
            return []

        return (self.pformat(value),)
