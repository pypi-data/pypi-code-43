
import os
import sys
import threading
import time
import traceback
from datetime import datetime

from pygments import highlight
# Taken from http://bzimmer.ziclix.com/2008/12/17/python-thread-dumps/
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.python import PythonLexer


def stacktraces():
    code = ["# Generation Timestamp: {}\n".format(datetime.now())]
    for threadId, stack in sys._current_frames().items():
        code.append("\n# ThreadID: %s" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))

    return highlight("\n".join(code), PythonLexer(), HtmlFormatter(
        full=False,
        # style="native",
        noclasses=True,
    ))


class TraceDumper(threading.Thread):
    """Dump stack traces into a given file periodically."""

    def __init__(self, fpath, interval, auto, *args, **kwargs):
        """
        @param fpath: File path to output HTML (stack trace file)
        @param auto: Set flag (True) to update trace continuously.
            Clear flag (False) to update only if file not exists.
            (Then delete the file to force update.)
        @param interval: In seconds: how often to update the trace file.
        """
        assert (interval > 0.1)
        self.auto = auto
        self.interval = interval
        self.fpath = os.path.abspath(fpath)
        self.stop_requested = threading.Event()

        super().__init__(*args, **kwargs)

    def run(self):
        while not self.stop_requested.isSet():
            time.sleep(self.interval)
            if self.auto or not os.path.isfile(self.fpath):
                with open(self.fpath, "wb+") as file:
                    file.write(stacktraces().encode())

    def stop(self):
        self.stop_requested.set()
        self.join()


_tracer = None


def trace_start(fpath, interval=1, auto=True):
    """Start tracing into the given file."""
    global _tracer
    if _tracer is None:
        _tracer = TraceDumper(fpath, interval, auto)
        _tracer.setDaemon(True)
        _tracer.start()


def trace_stop():
    """Stop tracing."""
    global _tracer
    if _tracer is None:
        raise Exception("Not tracing, cannot stop.")
    else:
        _tracer.stop()
