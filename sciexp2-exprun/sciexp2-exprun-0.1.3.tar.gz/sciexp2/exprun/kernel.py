#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2019, Lluís Vilanova"
__license__ = "GPL version 3 or later"


import logging
from . import wait

logger = logging.getLogger(__name__)


def check_version(shell, version, fail=True):
    """Check that a specific linux kernel version is installed.

    Parameters
    ----------
    shell
        Target shell.
    version : str
        Target kernel version.
    fail : bool, optional
        Whether to raise an exception when a different version is
        installed. Default is True.

    Returns
    -------
    bool
        Whether the target kernel version is installed.

    """
    res = shell.run(["uname", "-r"])
    current = res.output.split("\n")[0]
    if current == version:
        return True
    else:
        if fail:
            raise Exception("Invalid kernel version: target=%s current=%s" % (version, current))
        return False


def install_version(shell, version, package_base):
    """Install and reboot into a given linux kernel version if it is not the current.

    Parameters
    ----------
    shell
        Target shell.
    version : str
        Target kernel version.
    package_base : str
        Base directory in target shell where kernel packages can be installed
        from.

    """
    if check_version(shell, version, fail=False):
        return

    for name in ["linux-image-%(v)s_%(v)s-*.deb",
                 "linux-headers-%(v)s_%(v)s-*.deb",
                 "linux-libc-dev_%(v)s-*.deb"]:
        name = os.path.join(package_base, name % {"v": version})
        res = shell.run(["sh", "-c", "ls %s" % name])
        files = res.output.split("\n")
        for path in files:
            if path == "":
                continue
            logger.warn("Installing %s..." % path)
            shell.run(["sudo", "dpkg", "-i", path])

    res = shell.run(["grep", "-E", "menuentry .* %s" % version, "/boot/grub/grub.cfg"])
    grub_ids = res.output.split("\n")
    pattern = r" '([a-z0-9.-]+-%s-[a-z0-9.-]+)' {" % re.escape(version)
    grub_id = re.search(pattern, grub_ids[0]).group(1)

    with step("Updating GRUB %s..." % path, logger=logger.warn):
        shell.run(["sudo", "sed", "-i", "-e",
                   "s/^GRUB_DEFAULT=/GRUB_DEFAULT=\"saved\"/",
                   "/etc/default/grub"])
        shell.run(["sudo", "update-grub"])
        shell.run(["sudo", "grub-set-default", grub_id])

    with step("Rebooting into new kernel...", logger=logger.warn):
        shell.run(["sudo", "reboot"], allow_error=True)
        wait.ssh(shell)

    check_version(shell, version)


def check_cmdline(shell, arg):
    """Check the linux kernel was booted with the given commandline.

    Parameters
    ----------
    shell
        Target shell.
    arg : str
        Command line argument to check.

    """
    shell.run(["grep", arg, "/proc/cmdline"])


def check_module_param(shell, module, param, value, fail=True):
    """Check that a linux kernel module was loaded with the given parameter value.

    Parameters
    ----------
    shell
        Target shell.
    module : str
        Module name.
    param : str
        Module name.
    value
        Module value (will be coverted to str).
    fail : bool, optional
        Raise an exception if the value is not equal. Default is True.

    Returns
    -------
    bool
        Whether the given kernel module was loaded with the given parameter
        value.

    """
    with shell.open("/sys/module/%s/parameters/%s" % (module, param), "r") as f:
        f_val = f.read().split("\n")[0]
        if f_val != value:
            if fail:
                raise Exception("invalid kernel parameter value: target=%s current=%s" % (value, f_val))
            return False
        else:
            return True


__all__ = [
    "check_version", "install_version", "check_cmdline",
    "check_module_param",
]
