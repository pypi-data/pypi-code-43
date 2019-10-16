#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function
from __future__ import absolute_import

__author__     = "Lluís Vilanova"
__copyright__  = "Copyright 2019, Lluís Vilanova"
__license__    = "GPL version 3 or later"

__maintainer__ = "Lluís Vilanova"
__email__      = "llvilanovag@gmail.com"


import collections
import os
import re
import six


def get_tids(shell, pid, filter=None):
    """Get ids of all threads in a given process.

    Parameters
    ----------
    shell
        Target shell.
    pid : int
        Target process pid.
    filter : str or cre, optional
        Return pids that match given filter in process name. Default is all
        pids.

    Returns
    -------
    list of int
        List of the selected process pids.

    Notes
    -----
    When using a string for `filter` it will simply check it is part of the
    process name.

    """
    pids = shell.run(["ps", "H", "-o", "tid comm", str(pid)])
    lines = pids.output.split("\n")
    res = []
    for line in lines[1:]:
        line = line.strip()
        if line == "":
            continue
        pid, name = line.split(" ", 1)
        if filter:
            if isinstance(filter, six.string_types):
                if filter not in name:
                    continue
            else:
                if not filter.match(name):
                    continue
        res.append(int(pid))
    return res


def pin(shell, pid, cpus, **shell_kwargs):
    """Pin pid to given physical CPU list.

    Parameters
    ----------
    shell
        Target shell.
    pid : int
        Target pid or tid to pin.
    cpus : list of int
        Physical CPUs to pin the pid to.
    shell_kwargs : optional
        Arguments to `shell.run`

    """
    shell.run(["sudo", "taskset", "-p",
               "-c", ",".join(str(c) for c in cpus), str(pid)],
              **kwargs)


def cgroup_create(shell, controller, path, **kwargs):
    """Create a cgroup for given subsystem.

    Parameters
    ----------
    shell
        Target shell.
    controller : str
        Cgroup controller to configure.
    path : str
        New cgroup path.
    kwargs : dict
        Controller parameters to set. Lists are comma-concatenated, all elements
        are transformed to str.

    """
    shell.run(["sudo", "cgcreate", "-g", controller+":"+path])
    for key, val in kwargs.items():
        if isinstance(val, six.string_types) or not isinstance(val, collections.Iterable):
            val = [val]
        val = ",".join(str(v) for v in val)
        shell.run(["sudo", "cgset", "-r", "%s.%s=%s" % (controller, key, val), path])


def cgroup_pids(shell, path=None):
    """Get pids in given cgroup path.

    Parameters
    ----------
    shell
        Target shell.
    path : str, optional
        Cgroup path to analyze (defaults to entire system).

    Returns
    -------
    list of int
        Pids in the given cgroup.

    """
    res = set()
    base = "/sys/fs/cgroup"
    if path is None:
        path = ""
    cre = re.compile(os.path.join(base, "[^/]*", path))
    for dirpath, dirnames, filenames in os.walk(base):
        for filename in filenames:
            if filename == "tasks" and cre.match(dirpath):
                with open(os.path.join(dirpath, filename), "r") as f:
                    pids = (int(pid) for pid in f.read().split("\n")
                            if pid != "")
                    res.update(set(pids))
    return list(res)


def cgroup_move(shell, controller, path, pids):
    """Move pids to a cgroup.

    Parameters
    ----------
    shell
        Target shell.
    controller : str
        Cgroup controller.
    path : str
        Cgroup path.
    pids : pid or list of pid
        Pids to move into the cgroup. All elements are transformed to str.

    Notes
    -----
    If you move the process that is serving this shell, you might have to
    reconnect the shell to continue using it.

    """
    if isinstance(pids, six.string_types) or not isinstance(pids, collections.Iterable):
        pids = [pids]
    shell.run(["sudo", "cgclassify", "-g", "%s:%s" % (controller, path)] +
              [str(p) for p in pids
               if str(p) != ""])

__all__ = [
    "get_tids", "pin",
    "cgroup_create", "cgroup_pids", "cgroup_move",
]
