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
import re
from . import kernel


def set_freq(shell, path="cpupower", ld_library_path="", freq="max"):
    """Set frequency scaling.

    Parameters
    ----------
    shell
        Target shell.
    path : str, optional
        Path to cpupower tool. Default is use the cpupower tool in the PATH.
    ld_library_path : str, optional
        Library path to run cpupower tool. Default is use the system's library
        path.
    freq : str, optional
        Frequency to set in GHz. Default is use maximum frequency.

    """
    kernel.check_cmdline(shell, "intel_pstate=disable")

    if freq == "max":
        max_freq = shell.run([
            "sh", "-c",
            "sudo LD_LIBRARY_PATH=%s %s frequency-info | grep 'hardware limits' | sed -e 's/.* - \\(.*\\) GHz/\\1/'" % (
                ld_library_path, path)])
        freq = max_freq.output[:-1]

    shell.run(["sudo",
               "LD_LIBRARY_PATH=%s" % ld_library_path, path,
               "-c", "all", "frequency-set", "--governor", "userspace"])
    shell.run(["sudo",
               "LD_LIBRARY_PATH=%s" % ld_library_path, path,
               "-c", "all", "frequency-set", "--freq", freq + "GHz"])


def _get_mask(cpu_list):
    mask = 0
    for cpu in cpu_list:
        mask += 1 << cpu
    return mask

def set_irqs(shell, *irqs, **kwargs):
    """Make irqbalance ignore the given IRQs, and instead set their SMP affinity.

    Parameters
    ----------
    shell
        Target system.
    irqs
        IRQ descriptors.
    ignore_errors : bool, optional
        Ignore errors when manually setting an IRQ's SMP affinity. Implies that
        irqbalance will manage that IRQ. Default is False.
    irqbalance_banned_cpus : list of int, optional
        CPUs that irqbalance should not use for balancing.
    irqbalance_args : list of str, optional
        Additional arguments to irqbalance.

    Each descriptor in `irqs` is a three-element tuple:
    * Type: either ``irq`` for the first column in /proc/interrupts, or
            ``descr`` for the interrupt description after the per-CPU counts.
    * Regex: a regular expression to apply to the fields above, or `True` to
             apply to all values (a shorthand to the regex ".*"), or an `int` (a
             shorthand to the regex "^int_value$").
    * SMP affinity: list of cpu numbers to set as the IRQ's affinity; if `True`
                    is used instead, let irqbalance manage this IRQ.

    All matching descriptors are applied in order for each IRQ. If no descriptor
    matches, or the last matching descriptor has `True` as its affinity value,
    the IRQ will be managed by irqbalance as before.

    Returns
    -------
    The new irqbalance process.

    """
    ignore_errors = kwargs.pop("ignore_errors", False)
    irqbalance_args = kwargs.pop("irqbalance_args", [])
    irqbalance_banned_cpus = kwargs.pop("irqbalance_banned_cpus", [])
    irqbalance_banned_cpus_mask = _get_mask(irqbalance_banned_cpus)
    if len(kwargs) > 0:
        raise Exception("unknown argument: %s" % list(kwargs.keys())[0])

    irqs_parsed = []
    for arg_irq in irqs:
        if len(arg_irq) != 3:
            raise ValueError("wrong IRQ descriptor: %s" % repr(arg_irq))

        irq_type, irq_re, irq_cpus = arg_irq

        if isinstance(irq_re, int):
            irq_re = "^%d$" % irq_re
        if not isinstance(irq_re, bool) and not isinstance(irq_re, six.string_types):
            raise TypeError("wrong IRQ descriptor regex: %s" % str(irq_re))
        if not isinstance(irq_re, bool):
            irq_re = re.compile(irq_re)

        if (not isinstance(irq_cpus, bool) and (isinstance(irq_cpus, six.string_types) or
                                              not isinstance(irq_cpus, collections.Iterable))):
            raise TypeError("wrong IRQ descriptor CPU list: %s" % str(irq_cpus))

        if irq_type not in ["irq", "descr"]:
            raise ValueError("wrong IRQ descriptor type: %s" % str(irq_type))

        irqs_parsed.append((irq_type, irq_re, irq_cpus))

    irq_manual = []
    irqbalance_banned = set()

    cre = re.compile(r"(?P<irq>[^:]+):(?:\s+[0-9]+)+\s+(?P<descr>.*)")
    with shell.open("/proc/interrupts") as f:
        for line in f.read().split("\n"):
            match = cre.match(line)
            if match is None:
                continue

            irq = match.groupdict()["irq"].strip()
            descr = match.groupdict()["descr"].strip()

            cpus = True

            for irq_type, irq_cre, irq_cpus in irqs_parsed:
                if irq_type == "irq":
                    if irq_cre == True or irq_cre.match(irq):
                        cpus = irq_cpus
                elif irq_type == "descr":
                    if irq_cre == True or irq_cre.match(descr):
                        cpus = irq_cpus
                else:
                    assert False, irq_type

            if cpus != True:
                irq_manual.append((irq, cpus))
                irqbalance_banned.add(irq)

    for irq, cpus in irq_manual:
        mask = _get_mask(cpus)
        try:
            shell.run(["sudo", "sh", "-c",
                       "echo %x > /proc/irq/%s/smp_affinity" % (irq, mask)])
        except:
            if ignore_errors:
                irqbalance_banned.remove(irq)
            else:
                raise

    shell.run(["sudo", "service", "irqbalance", "stop"])
    proc = shell.spawn(["sudo", "IRQBALANCE_BANNED_CPUS=%x" % irqbalance_banned_cpus_mask,
                        "irqbalance"] + irqbalance_args +
                       ["--banirq=%s" % banned
                        for banned in irqbalance_banned],
                       encoding="ascii")
    return proc


def get_cpus(shell, node=None, package=None, core=None, pu=None, cgroup=None):
    """Get a set of all physical CPU indexes in the system.

    It uses the hwloc-calc program to report available CPUs.

    Parameters
    ----------
    shell
        Target shell.
    node : int or str, optional
        NUMA nodes to check. Defaults to all.
    package : int or str, optional
        Core packages to check on selected NUMA nodes. Defaults to all.
    core : int or str, optional
        Cores to check on selected core packages. Defaults to all.
    pu : int or str, optional
        PUs to check on selected cores. Defaults to all.
    cgroup : str, optional
        Cgroup path.

    Returns
    -------
    set of int
        Physical CPU indexes (as used by Linux).

    Notes
    -----
    The combination of all the arguments is a flexible way to get all the
    information in the system. Each of these arguments can have any of the forms
    described under "Hwloc Indexes" in manpage hwloc(7). A few examples.

    Second thread of each core:
    >>> get_cpus(shell, pu=1)

    First thread of each core in first NUMA node:
    >>> get_cpus(node=0, pu=0)

    Hardware threads in first core of the entire system:
    >>> get_cpus(node=0, package=0, core=0)

    """
    cmd = ["hwloc-calc", "--intersect", "PU",
           "--li", "--po", ""]

    def add_level(name, value):
        if value is not None:
            cmd[-1] += ".%s:%s" % (name, str(value))
    add_level("node", node)
    add_level("package", package)
    add_level("core", core)
    add_level("pu", pu)
    if cmd[-1] == "":
        cmd[-1] = "all"
    else:
        cmd[-1] = cmd[-1][1:]

    if cgroup is not None:
        cmd = ["sudo", "cgexec", "-g", cgroup] + cmd

    res = shell.run(cmd, encoding="ascii")
    line = res.output.split("\n")[0]
    if line == "":
        raise ValueError("hwloc-calc: %r" % res.stderr_output)
    return [int(i) for i in res.output.split(",")]


__all__ = [
    "set_freq", "set_irqs", "get_cpus",
]
