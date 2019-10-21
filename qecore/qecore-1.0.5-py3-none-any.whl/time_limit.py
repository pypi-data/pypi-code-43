#!/usr/bin/env python3
import contextlib
import errno
import os
import signal

DEFAULT_MESSAGE = os.strerror(errno.ETIME)

class QETimeoutError(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


class Timeout(contextlib.ContextDecorator):
    def __init__(self, seconds, timeout_message=DEFAULT_MESSAGE, suppress_timeout_errors=False):
        self.seconds = int(seconds)
        self.timeout_message = timeout_message
        self.suppress = bool(suppress_timeout_errors)

    def _timeout_handler(self, signum, frame):
        raise QETimeoutError(self.timeout_message)

    def __enter__(self):
        signal.signal(signal.SIGALRM, self._timeout_handler)
        signal.alarm(self.seconds)

    def __exit__(self, exception_type, exception_valeu, exception_traceback):
        signal.alarm(0)
        if self.suppress and exception_type is QETimeoutError:
            return
