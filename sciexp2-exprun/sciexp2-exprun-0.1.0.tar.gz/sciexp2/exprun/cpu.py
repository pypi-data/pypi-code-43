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
                        for banned in irqbalance_banned])
    return proc


def get_cpus(shell, node=None, package=None, core=None, pu=None, cgroup=None):
    """Get a set of all physical CPU indexes in the system.

    It uses the hwloc program to report available CPUs.

    Parameters
    ----------
    shell
        Target shell.
    node : int or list of int, optional
        NUMA nodes to check. Defaults to all.
    package : int or list of int, optional
        Core packages to check on selected NUMA nodes. Defaults to all.
    core : int or list of int, optional
        Cores to check on selected core packages. Defaults to all.
    pu : int or list of int, optional
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
    information in the system. A few examples.

    Second thread of each core:
    >>> get_cpus(shell, pu=1)

    First thread of each core in first NUMA node:
    >>> get_cpus(node=0, pu=0)

    Hardware threads in first core of the entire system:
    >>> get_cpus(node=0, package=0, core=0)

    """
    cmd = ["hwloc-ls", "--no-caches", "-c"]
    if cgroup is not None:
        cmd = ["sudo", "cgexec", "-g", cgroup] + cmd
    res = shell.run(cmd)
    lines = res.output.split("\n")

    # parse output

    def get_mask(line):
        parts = line.split("cpuset=")
        mask = parts[-1]
        return int(mask, base=16)

    def get_set(line):
        mask = get_mask(line)
        bin_mask = bin(mask)[2:]
        res = set()
        for idx, i in enumerate(reversed(bin_mask)):
            if i == "1":
                res.add(idx)
        return res

    root = []
    for line in lines:
        parts = line.strip().split(" ")
        if parts[0] == "NUMANode":
            target = root
            target.append([])
        elif parts[0] == "Package":
            target = root[-1]
            target.append([])
        elif parts[0] == "Core":
            target = root[-1]
            target = target[-1]
            target.append([])
        elif parts[0] == "PU":
            pus = get_set(parts[-1])
            target = root[-1]
            target = target[-1]
            target = target[-1]
            target.append(pus)

    # compute PU set

    def reduce_or(arg):
        res = set()
        for a in arg:
            res |= a
        return res

    def collect(level, target, parents):
        indexes = target[0]

        if indexes is None:
            indexes = range(len(level))
        elif isinstance(indexes, int):
            indexes = [indexes]

        if isinstance(indexes, collections.Iterable):
            res = set()
            for idx in indexes:
                try:
                    s = level[idx]
                except IndexError:
                    parent_names = ["node", "package", "core", "pu"]
                    path = zip(parent_names, parents+[idx])
                    raise Exception("invalid cpu path: %s" % " ".join(
                        "%s=%d" % (n, i) for n, i in path))
                else:
                    if len(target) == 1:
                        res |= s
                    else:
                        res |= collect(s, target[1:], parents+[idx])
            return res
        else:
            assert False, value

    res = collect(root, [node, package, core, pu], [])
    return res

__all__ = [
    "set_freq", "set_irqs", "get_cpus",
]
