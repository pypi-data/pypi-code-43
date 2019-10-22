#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Functions to wait on remote connections and process output."""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2019, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import re
import io
import time
from . import spur


def run(shell, *args, **kwargs):
    """Run command with a timeout.

    Parameters
    ----------
    shell
       Shell used to run given command.
    timeout : int, optional
       Timeout before erroring out (in seconds). Default is no timeout.
    rerun_error : bool, optional
       Rerun command every time it fails. Default is False.
    args, kwargs
       Paramaters to the shell's spawn method.

    Returns
    -------
    spur.ExecutionResult

    """
    timeout = kwargs.pop("timeout", 0)
    rerun_error = kwargs.pop("rerun_error", False)
    allow_error = kwargs.pop("allow_error", False)

    proc = None
    t_start = time.time()

    while True:
        t_now = time.time()
        if t_now - t_start > timeout > 0:
            raise Exception("Wait timed out" + repr((t_now - t_start, timeout)))
        if proc is None:
            proc = shell.spawn(*args, allow_error=True, **kwargs)
        if proc.is_running():
            time.sleep(2)
        else:
            res = proc.wait_for_result()
            if res.return_code == 0:
                return res
            if not allow_error:
                if rerun_error:
                    proc = None
                    time.sleep(2)
                else:
                    raise res.to_error()
            else:
                return res


def connection(shell, address, port, timeout=0):
    """Wait until we can connect to given address/port."""
    cmd = ["sh", "-c", "echo | nc %s %d" % (address, port)]
    run(shell, cmd, timeout=timeout, rerun_error=True)


def ssh(shell, timeout=0):
    """Wait until we can ssh through given shell."""
    if spur.is_local_shell(shell):
        return
    local = spur.LocalShell()
    cmd = [
        # pylint: disable=protected-access
        "sshpass", "-p", shell._password,
        "ssh",
        "-o", "ConnectTimeout=1",
        "-o", "StrictHostKeyChecking=no",
        # pylint: disable=protected-access
        "-p", str(shell._port), shell.username+"@"+shell.hostname,
        "true",
    ]
    run(local, cmd, timeout=timeout, rerun_error=True)


def print_stringio(obj, out=None):
    """Print contents of a StringIO object as they become available.

    Useful in combination with `stringio` to print an output while processing
    it.

    Parameters
    ----------
    obj : StringIO
        StringIO object to print.
    out : file or function, optional
        File or function to print object's contents. Defaults to stdout.

    Examples
    --------
    >>> stdout = StringIO.StringIO()
    >>> thread.start_new_thread(print_stringio, (stdout,))
    >>> shell.run(["sh", "-c", "sleep 1 ; echo start ; sleep 2; echo end ; sleep 1"],
    ...           stdout=stdout)
    start
    end

    See also
    --------
    stringio

    """
    if not isinstance(obj, io.StringIO):
        raise TypeError("expected a StringIO object")
    if callable(out):
        def flush():
            pass
    else:
        def flush():
            if out is not None:
                out.flush()
        # pylint: disable=invalid-name
        def f(message):
            print(message, end="", out=out)
        out = f
    seen = 0
    while True:
        time.sleep(0.5)
        contents = obj.getvalue()
        missing = contents[seen:]
        if missing:
            out(missing)
            flush()
            seen += len(missing)


def stringio(obj, pattern):
    """Wait until a StringIO's contents match the given regex.

    Useful to trigger operations when a process generates certain output.

    Examples
    --------
    Count time between the "start" and "end" lines printed by a process:

    >>> stdout = io.StringIO()
    >>> def timer(obj):
            stringio(obj, "^start$")
            t_start = time.time()
            stringio(obj, "^end$")
            t_end = time.time()
            print("time:", int(t_end - t_start))
    >>> thread.start_new_thread(timer, (stdout,))
    >>> shell.run(["sh", "-c", "sleep 1 ; echo start ; sleep 2; echo end ; sleep >>> 1"],
    ...           stdout=stdout)
    time: 2

    See also
    --------
    print_stringio

    """
    if not isinstance(obj, io.StringIO):
        raise TypeError("expected a StringIO object")
    cre = re.compile(pattern, re.MULTILINE)
    while True:
        time.sleep(0.5)
        contents = obj.getvalue()
        match = cre.findall(contents)
        if match:
            return


__all__ = [
    "run", "connection", "ssh", "print_stringio", "stringio",
]
