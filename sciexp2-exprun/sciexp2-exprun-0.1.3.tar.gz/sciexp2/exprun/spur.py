#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Extensions to external `spur` package."""

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2019, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import atexit
import collections
import logging
import os
import signal
import sys
import threading
import time
import traceback

import six
import spur
import spur.ssh


_LOGGER = logging.getLogger(__name__)


def is_local_shell(shell):
    """Whether the given shell is a `spur.LocalShell` or derivative."""
    return isinstance(shell, spur.LocalShell)


def is_ssh_shell(shell):
    """Whether the given shell is a `spur.SshShell` or derivative."""
    return isinstance(shell, spur.SshShell)


# Patch spur to update the _is_killed attribute when sending signals
def _patch_send_signal(func):
    def send_signal_wrapper(self, signum):
        if signum in [signal.SIGINT, signal.SIGQUIT, signal.SIGKILL]:
            # pylint: disable=protected-access
            self._is_killed = True
        return func(self, signum)
    return send_signal_wrapper
spur.ssh.SshProcess.send_signal = _patch_send_signal(spur.ssh.SshProcess.send_signal)


# Monitor background processes for failures, so we can error out early

_EXITING = False
_LOCK = threading.RLock()


def _kill_all():
    # pylint: disable=global-statement
    global _EXITING
    _EXITING = True
    # pylint: disable=protected-access
    LocalShell._atexit_cb()
    # pylint: disable=protected-access
    SshShell._atexit_cb()


atexit.register(_kill_all)


# pylint: disable=invalid-name,too-few-public-methods
class with_pid:
    """Decorator to define a kill argument that takes the process' pid.

    To be used as an element in the `kill` argument to a shell's `run` or
    `spawn` method::

        shell.run(["sudo", "program"], kill=["sudo", "kill", with_pid()])

    Can be used in three ways, depending on the type of `func`:
    - `None`: replace with the stringified process pid.
    - `str`: format with the process' pid with the ``pid`` key.
    - otherwise: call with the pid as an argument.

    """
    def __init__(self, func=None):
        self._func = func
    def __call__(self, pid):
        if self._func is None:
            return str(pid)
        if isinstance(self._func, six.string_types):
            return self._func.format(pid=pid)
        return self._func(pid)

def _kill_pid(shell, pid, kill_args):
    if kill_args:
        args = []
        for arg in kill_args:
            if isinstance(arg, with_pid):
                args.append(arg(pid))
            else:
                args.append(arg)
        shell.run(args)
    else:
        shell.run(["pkill", "-P", str(pid)])


def _print_traceback(cmd_msg, stack_info=None):
    if stack_info is None:
        stack_info = traceback.extract_stack()
    stack_idx = 0 if stack_info[0][2] == "<module>" else 6
    print("Traceback (most recent call last):")
    msg = traceback.format_list(stack_info[stack_idx:-1])
    print("".join(msg), end="")
    exc_type, exc_value, tb = sys.exc_info()
    info = traceback.extract_tb(tb)
    msg = traceback.format_list(info)
    print("".join(msg), end="")
    print("%s.%s: %s" % (exc_type.__module__, exc_type.__name__, exc_value))
    print("command:", cmd_msg)


def _watchdog_thread(shell, obj, cmd_msg, exit_on_error):
    stack_info = traceback.extract_stack()
    def watchdog():
        while obj.is_running():
            time.sleep(1)
        try:
            obj.wait_for_result()
        # pylint: disable=bare-except
        except:
            # pylint: disable=protected-access
            shell._child_remove(obj)
            _LOGGER.info("- %s", cmd_msg)
            # pylint: disable=protected-access
            if not obj._is_killed and not _EXITING:
                _print_traceback(cmd_msg, stack_info)
                if exit_on_error:
                    _kill_all()
                    os._exit(1)
        else:
            shell._child_remove(obj)    # pylint: disable=protected-access
            _LOGGER.info("- %s", cmd_msg)
    thread = threading.Thread(target=watchdog)
    thread.daemon = True
    thread.start()


# pylint: disable=function-redefined
class LocalShell(spur.LocalShell):
    """An extended version of `spur.LocalShell`.

    It will properly kill all created processes when exiting.

    The `run` and `spawn` methods have two new arguments:

    - ``exit_on_error``: bool, optional
          Whether to exit the program when the process fails to execute.

    - ``kill``: list of str, optional
          Command to execute when killing the process. Useful when process is
          run with sudo.

    """

    __CHILDREN = collections.OrderedDict()

    def _child_add(self, obj, kill):
        with _LOCK:
            LocalShell.__CHILDREN[obj] = (self, kill)

    @classmethod
    def _child_remove(cls, obj):
        with _LOCK:
            del cls.__CHILDREN[obj]

    # pylint: disable=arguments-differ
    def run(self, *args, **kwargs):
        process = self.spawn(*args, **kwargs, exit_on_error=False)
        result = process.wait_for_result()
        return result

    def spawn(self, *args, **kwargs):
        exit_on_error = kwargs.pop("exit_on_error", True)
        kill = kwargs.pop("kill", None)
        cmd = args[0]
        cmd_msg = " ".join(cmd)
        _LOGGER.info("+ %s", cmd_msg)
        try:
            obj = spur.LocalShell.spawn(self, *args, **kwargs, store_pid=True)
        # pylint: disable=bare-except
        except:
            if exit_on_error:
                stack_info = traceback.extract_stack()
                _print_traceback(cmd_msg, stack_info)
                _kill_all()
                # pylint: disable=protected-access
                os._exit(1)
            else:
                raise
        else:
            obj._is_killed = False      # pylint: disable=protected-access
            self._child_add(obj, kill)
            _watchdog_thread(self, obj, cmd_msg, exit_on_error)
            return obj

    @classmethod
    def _atexit_cb(cls):
        while True:
            with _LOCK:
                if not cls.__CHILDREN:
                    return
                child, (shell, kill) = next(iter(cls.__CHILDREN.items()))
                # pylint: disable=protected-access
                child._is_killed = True
                if child.is_running():
                    try:
                        _kill_pid(shell, child.pid, kill)
                        child.wait_for_result()
                    # pylint: disable=bare-except
                    except:
                        pass
                else:
                    try:
                        cls._child_remove(child)
                    # pylint: disable=bare-except
                    except:
                        pass


class SshShell(spur.SshShell):
    """An extended version of `spur.SshShell`.

    It will properly kill all created processes when exiting.

    The shell object has two new members:

    - ``hostname``: str
          Target host name.

    - ``username``: str
          Target user name.

    The `run` and `spawn` methods have two new arguments:

    - ``exit_on_error``: bool, optional
          Whether to exit the program when the process fails to execute.

    - ``kill``: list of str, optional
          Command to execute when killing the process. Useful when process is
          run with sudo.

    """

    __CHILDREN = collections.OrderedDict()

    def _child_add(self, obj, kill):
        with _LOCK:
            SshShell.__CHILDREN[obj] = (self, kill)

    @classmethod
    def _child_remove(cls, obj):
        with _LOCK:
            del cls.__CHILDREN[obj]

    def __init__(self, *args, **kwargs):
        spur.SshShell.__init__(self, *args, **kwargs)
        self.hostname = self._hostname
        self.username = self._username

    # pylint: disable=arguments-differ
    def run(self, *args, **kwargs):
        process = self.spawn(*args, **kwargs, exit_on_error=False)
        result = process.wait_for_result()
        return result

    # pylint: disable=arguments-differ
    def spawn(self, *args, **kwargs):
        exit_on_error = kwargs.pop("exit_on_error", True)
        kill = kwargs.pop("kill", None)
        cmd = args[0]
        cmd_msg = "ssh -p %d %s@%s %s" % (self._port, self.username, self.hostname, " ".join(cmd))
        _LOGGER.info("+ %s", cmd_msg)
        try:
            obj = spur.SshShell.spawn(self, *args, **kwargs, store_pid=True)
        # pylint: disable=bare-except
        except:
            if exit_on_error:
                stack_info = traceback.extract_stack()
                _print_traceback(cmd_msg, stack_info)
                _kill_all()
                # pylint: disable=protected-access
                os._exit(1)
            else:
                raise
        else:
            obj._is_killed = False      # pylint: disable=protected-access
            # pylint: disable=protected-access
            self._child_add(obj, kill)
            _watchdog_thread(self, obj, cmd_msg, exit_on_error)
            return obj

    @classmethod
    def _atexit_cb(cls):
        while True:
            with _LOCK:
                if not cls.__CHILDREN:
                    return
                child, (shell, kill) = next(iter(cls.__CHILDREN.items()))
                # pylint: disable=protected-access
                child._is_killed = True
                if child.is_running():
                    try:
                        _kill_pid(shell, child.pid, kill)
                        child.wait_for_result()
                    # pylint: disable=bare-except
                    except:
                        pass
                else:
                    try:
                        cls._child_remove(child)
                    # pylint: disable=bare-except
                    except:
                        pass


def get_shell(server, user=None, password=None, port=22):
    """Get a new shell.

    If `server` is a spur shell, return that instead.

    Parameters
    ----------
    server : str or object
    user : str, optional
    password : str, optional
    port : int, optional

    """
    if is_ssh_shell(server) or is_local_shell(server):
        return server
    return SshShell(hostname=server,
                    username=user,
                    password=password,
                    port=port,
                    missing_host_key=spur.ssh.MissingHostKey.accept)

__all__ = [
    "is_local_shell", "is_ssh_shell", "get_shell",
    "with_pid",
]

__all__ += spur.__all__
