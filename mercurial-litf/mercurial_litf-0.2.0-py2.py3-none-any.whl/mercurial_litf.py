# -*- coding: utf-8 -*-

"""Main module."""
from __future__ import absolute_import, print_function

import argparse
import collections
import difflib
import distutils.version as version
import errno
import json
import os
import random
import re
import shutil
import signal
import socket
import subprocess
import sys
import sysconfig
import tempfile
import threading
import time
import unittest
import xml.dom.minidom as minidom

try:
    import Queue as queue
except ImportError:
    import queue

try:
    import shlex

    shellquote = shlex.quote
except (ImportError, AttributeError):
    import pipes

    shellquote = pipes.quote

if os.environ.get("RTUNICODEPEDANTRY", False):
    try:
        reload(sys)
        sys.setdefaultencoding("undefined")
    except NameError:
        pass

origenviron = os.environ.copy()
osenvironb = getattr(os, "environb", os.environ)
processlock = threading.Lock()

pygmentspresent = False
# ANSI color is unsupported prior to Windows 10
if os.name != "nt":
    try:  # is pygments installed
        import pygments
        import pygments.lexers as lexers
        import pygments.lexer as lexer
        import pygments.formatters as formatters
        import pygments.token as token
        import pygments.style as style

        pygmentspresent = True
        difflexer = lexers.DiffLexer()
        terminal256formatter = formatters.Terminal256Formatter()
    except ImportError:
        pass

if pygmentspresent:

    class TestRunnerStyle(style.Style):
        default_style = ""
        skipped = token.string_to_tokentype("Token.Generic.Skipped")
        failed = token.string_to_tokentype("Token.Generic.Failed")
        skippedname = token.string_to_tokentype("Token.Generic.SName")
        failedname = token.string_to_tokentype("Token.Generic.FName")
        styles = {
            skipped: "#e5e5e5",
            skippedname: "#00ffff",
            failed: "#7f0000",
            failedname: "#ff0000",
        }

    class TestRunnerLexer(lexer.RegexLexer):
        testpattern = r"[\w-]+\.(t|py)(#[^\s]+)?"
        tokens = {
            "root": [
                (r"^Skipped", token.Generic.Skipped, "skipped"),
                (r"^Failed ", token.Generic.Failed, "failed"),
                (r"^ERROR: ", token.Generic.Failed, "failed"),
            ],
            "skipped": [
                (testpattern, token.Generic.SName), (r":.*", token.Generic.Skipped)
            ],
            "failed": [
                (testpattern, token.Generic.FName), (r"(:| ).*", token.Generic.Failed)
            ],
        }

    runnerformatter = formatters.Terminal256Formatter(style=TestRunnerStyle)
    runnerlexer = TestRunnerLexer()

if sys.version_info > (3, 5, 0):
    PYTHON3 = True
    xrange = range  # we use xrange in one place, and we'd rather not use range

    def _bytespath(p):
        if p is None:
            return p
        return p.encode("utf-8")

    def _strpath(p):
        if p is None:
            return p
        return p.decode("utf-8")


elif sys.version_info >= (3, 0, 0):
    print(
        "%s is only supported on Python 3.5+ and 2.7, not %s"
        % (sys.argv[0], ".".join(str(v) for v in sys.version_info[:3]))
    )
    sys.exit(70)  # EX_SOFTWARE from `man 3 sysexit`
else:
    PYTHON3 = False

    # In python 2.x, path operations are generally done using
    # bytestrings by default, so we don't have to do any extra
    # fiddling there. We define the wrapper functions anyway just to
    # help keep code consistent between platforms.
    def _bytespath(p):
        return p

    _strpath = _bytespath

# For Windows support
wifexited = getattr(os, "WIFEXITED", lambda x: False)

PYTHON = _bytespath(sys.executable.replace("\\", "/"))
IMPL_PATH = b"PYTHONPATH"
if "java" in sys.platform:
    IMPL_PATH = b"JYTHONPATH"

defaults = {
    "jobs": ("HGTEST_JOBS", 1),
    "timeout": ("HGTEST_TIMEOUT", 180),
    "slowtimeout": ("HGTEST_SLOWTIMEOUT", 500),
    "port": ("HGTEST_PORT", 20059),
    "shell": ("HGTEST_SHELL", "sh"),
}


def canonpath(path):
    return os.path.realpath(os.path.expanduser(path))


def parselistfiles(files, listtype, warn=True):
    entries = dict()
    for filename in files:
        try:
            path = os.path.expanduser(os.path.expandvars(filename))
            f = open(path, "rb")
        except IOError as err:
            if err.errno != errno.ENOENT:
                raise
            if warn:
                print("warning: no such %s file: %s" % (listtype, filename))
            continue

        for line in f.readlines():
            line = line.split(b"#", 1)[0].strip()
            if line:
                entries[line] = filename

        f.close()
    return entries


def parsettestcases(path):
    """read a .t test file, return a set of test case names

    If path does not exist, return an empty set.
    """
    cases = set()
    try:
        with open(path, "rb") as f:
            for l in f:
                if l.startswith(b"#testcases "):
                    cases.update(l[11:].split())
    except IOError as ex:
        if ex.errno != errno.ENOENT:
            raise
    return cases


def rename(src, dst):
    """Like os.rename(), trade atomicity and opened files friendliness
    for existing destination support.
    """
    shutil.copy(src, dst)
    os.remove(src)


_unified_diff = difflib.unified_diff
if PYTHON3:
    import functools

    _unified_diff = functools.partial(difflib.diff_bytes, difflib.unified_diff)


def getdiff(expected, output, ref, err):
    servefail = False
    lines = []
    for line in _unified_diff(expected, output, ref, err):
        if line.startswith(b"+++") or line.startswith(b"---"):
            line = line.replace(b"\\", b"/")
            if line.endswith(b" \n"):
                line = line[:-2] + b"\n"
        lines.append(line)
        if (
            not servefail
            and line.startswith(b"+  abort: child process failed to start")
        ):
            servefail = True

    return servefail, lines


verbose = False


def vlog(*msg):
    """Log only when in verbose mode."""
    if verbose is False:
        return

    return log(*msg)


# Bytes that break XML even in a CDATA block: control characters 0-31
# sans \t, \n and \r
CDATA_EVIL = re.compile(br"[\000-\010\013\014\016-\037]")

# Match feature conditionalized output lines in the form, capturing the feature
# list in group 2, and the preceeding line output in group 1:
#
#   output..output (feature !)\n
optline = re.compile(b"(.*) \((.+?) !\)\n$")


def cdatasafe(data):
    """Make a string safe to include in a CDATA block.

    Certain control characters are illegal in a CDATA block, and
    there's no way to include a ]]> in a CDATA either. This function
    replaces illegal bytes with ? and adds a space between the ]] so
    that it won't break the CDATA block.
    """
    return CDATA_EVIL.sub(b"?", data).replace(b"]]>", b"] ]>")


def log(*msg):
    """Log something to stdout.

    Arguments are strings to print.
    """
    with iolock:
        if verbose:
            print(verbose, end=" ")
        for m in msg:
            print(m, end=" ")
        print()
        sys.stdout.flush()


def highlightdiff(line, color):
    if not color:
        return line
    assert pygmentspresent
    return pygments.highlight(
        line.decode("latin1"), difflexer, terminal256formatter
    ).encode(
        "latin1"
    )


def highlightmsg(msg, color):
    if not color:
        return msg
    assert pygmentspresent
    return pygments.highlight(msg, runnerlexer, runnerformatter)


def terminate(proc):
    """Terminate subprocess"""
    vlog("# Terminating process %d" % proc.pid)
    try:
        proc.terminate()
    except OSError:
        pass


# Some glob patterns apply only in some circumstances, so the script
# might want to remove (glob) annotations that otherwise should be
# retained.
checkcodeglobpats = [
    # On Windows it looks like \ doesn't require a (glob), but we know
    # better.
    re.compile(br"^pushing to \$TESTTMP/.*[^)]$"),
    re.compile(br"^moving \S+/.*[^)]$"),
    re.compile(br"^pulling from \$TESTTMP/.*[^)]$"),
    # Not all platforms have 127.0.0.1 as loopback (though most do),
    # so we always glob that too.
    re.compile(br".*\$LOCALIP.*$"),
]

bchr = chr
if PYTHON3:
    bchr = lambda x: bytes([x])

iolock = threading.RLock()
firstlock = threading.RLock()
firsterror = False


class TestResult(unittest._TextTestResult):
    """Holds results when executing via unittest."""
    # Don't worry too much about accessing the non-public _TextTestResult.
    # It is relatively common in Python testing tools.
    def __init__(self, options, *args, **kwargs):
        self.start = time.time()
        super(TestResult, self).__init__(*args, **kwargs)

        self._options = options

        # unittest.TestResult didn't have skipped until 2.7. We need to
        # polyfill it.
        self.skipped = []

        # We have a custom "ignored" result that isn't present in any Python
        # unittest implementation. It is very similar to skipped. It may make
        # sense to map it into skip some day.
        self.ignored = []

        self.times = []
        self._firststarttime = None
        # Data stored for the benefit of generating xunit reports.
        self.successes = []
        self.faildata = {}

        self.start = None
        self.stop = None

        if options.color == "auto":
            self.color = pygmentspresent and self.stream.isatty()
        elif options.color == "never":
            self.color = False
        else:  # 'always', for testing purposes
            self.color = pygmentspresent

    def onStart(self, tests):
        if hasattr(tests, "_tests"):
            test_number = len(tests._tests)
        else:
            test_number = len(tests)
        with iolock:
            print(json.dumps({"_type": "session_start", "test_number": test_number}))

    def onEnd(self):
        self.stop = time.time()
        data = {
            "skipped": 0,
            "failed": 0,
            "error": 0,
            "total_duration": self.stop - self.start,
            "passed": 0,
            "_type": "session_end",
        }

        with iolock:
            print(json.dumps(data))

    def addFailure(self, test, reason):
        self.failures.append((test, reason))
        if reason == "output changed":
            # Ignore output changed as we should already displayed it
            return

        if self._options.first:
            self.stop()
        else:
            with iolock:
                if reason == "timed out":
                    self.stream.write("t")
                else:
                    if not self._options.nodiff:
                        self.stream.write("\n")
                        # Exclude the '\n' from highlighting to lex correctly
                        formatted = "ERROR: %s output changed\n" % test
                        self.stream.write(highlightmsg(formatted, self.color))
                    self.stream.write("!")

                self.stream.flush()

    def addSuccess(self, test):
        if test._finished is None:
            return self._add_collection(test)

        # print("ADD SUCCESS", test, repr(test), test.__dict__)

        starttime = test.started
        # endtime = test.stopped
        endtime = os.times()
        real_time = endtime[4] - starttime[4]

        data = {
            "stderr": "",
            "_type": "test_result",
            "skipped_messages": {},
            "outcome": "passed",
            "durations": {},
            "duration": real_time,
            "line": 1,
            "file": test.bname,
            "error": {"humanrepr": ""},
            "test_name": test.name,
            "stdout": "",
            "id": test.name,
        }

        with iolock:
            print(json.dumps(data))

        self.successes.append(test)

    def _add_collection(self, test):
        data = {
            "_type": "test_collection",
            "test_name": test.name,
            "id": test.name,
            "file": test.bname,
            "line": 0,
        }

        with iolock:
            print(json.dumps(data))

    def addError(self, test, err):
        starttime = test.started
        # endtime = test.stopped
        endtime = os.times()
        real_time = endtime[4] - starttime[4]

        data = {
            "stderr": "",
            "_type": "test_result",
            "skipped_messages": {},
            "outcome": "failed",
            "durations": {},
            "duration": real_time,
            "line": 1,
            "file": test.bname,
            "error": {"humanrepr": str(err)},
            "test_name": test.name,
            "stdout": "",
            "id": test.name,
        }

        print(json.dumps(data))
        # super(TestResult, self).addError(test, err)
        if self._options.first:
            self.stop()

    # Polyfill.
    def addSkip(self, test, reason):
        starttime = test.started
        # endtime = test.stopped
        endtime = os.times()
        real_time = endtime[4] - starttime[4]

        data = {
            "stderr": "",
            "_type": "test_result",
            "skipped_messages": {"test": reason},
            "outcome": "skipped",
            "durations": {},
            "duration": real_time,
            "line": 1,
            "file": test.bname,
            "error": {"humanrepr": ""},
            "test_name": test.name,
            "stdout": "",
            "id": test.name,
        }
        print(json.dumps(data))
        self.skipped.append((test, reason))

    def addIgnore(self, test, reason):
        self.ignored.append((test, reason))
        with iolock:
            if self.showAll:
                self.stream.writeln("ignored %s" % reason)
            else:
                if reason not in ("not retesting", "doesn't match keyword"):
                    self.stream.write("i")
                else:
                    self.testsRun += 1
                self.stream.flush()

    def addOutputMismatch(self, test, ret, got, expected):
        """Record a mismatch in test output for a particular test."""
        if self.shouldStop or firsterror:
            # don't print, some other test case already failed and
            # printed, we're just stale and probably failed due to our
            # temp dir getting cleaned up.
            return

        starttime = test.started
        # endtime = test.stopped
        endtime = os.times()
        real_time = endtime[4] - starttime[4]

        _, lines = getdiff(expected, got, test.refpath, test.errpath)

        data = {
            "stderr": "",
            "_type": "test_result",
            "skipped_messages": {},
            "outcome": "failed",
            "durations": {},
            "duration": real_time,
            "line": 1,
            "file": test.bname,
            "error": {"diff": {"got": got, "expected": expected, "diff": lines}},
            "test_name": test.name,
            "stdout": "",
            "id": test.name,
        }
        print(json.dumps(data))

    def startTest(self, test):
        super(TestResult, self).startTest(test)

        # os.times module computes the user time and system time spent by
        # child's processes along with real elapsed time taken by a process.
        # This module has one limitation. It can only work for Linux user
        # and not for Windows.
        test.started = os.times()
        if self._firststarttime is None:  # thread racy but irrelevant
            self._firststarttime = test.started[4]

    def stopTest(self, test, interrupted=False):
        super(TestResult, self).stopTest(test)

        test.stopped = os.times()

        starttime = test.started
        endtime = test.stopped
        origin = self._firststarttime
        self.times.append(
            (
                test.name,
                endtime[2] - starttime[2],  # user space CPU time
                endtime[3] - starttime[3],  # sys  space CPU time
                endtime[4] - starttime[4],  # real time
                starttime[4] - origin,  # start date in run context
                endtime[4] - origin,  # end date in run context
            )
        )

        if interrupted:
            with iolock:
                self.stream.writeln(
                    "INTERRUPTED: %s (after %d seconds)"
                    % (test.name, self.times[-1][3])
                )
