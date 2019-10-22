#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = "Lluís Vilanova"
__copyright__ = "Copyright 2019, Lluís Vilanova"
__license__ = "GPL version 3 or later"


from . import spur


def install(shell, package):
    """Install given `package` using `shell`."""
    if spur.is_ssh_shell(shell):
        hostname = shell.hostname
    else:
        hostname = "localhost"
    shell.run([
        "bash", "-c",
        "dpkg -s %s >/dev/null 2>&1 || sudo apt-get install -y %s" % (package,
                                                                      package),
    ])


def install_deps(shell):
    """Install all needed system packages.

    Must be called on a local shell before using other functions that require a
    shell, and before using other functions through the same shell.

    Parameters
    ----------
    shell
        Target system.

    """
    install(shell, "cgroup-tools")
    install(shell, "hwloc")
    install(shell, "rsync")
    install(shell, "netcat-traditional")
    install(shell, "psmisc")
    install(shell, "util-linux")


def rsync(src_shell, src_path, dst_shell, dst_path, run_shell=None, args=[]):
    """Synchronize two directories using rsync.

    Parameters
    ----------
    src_shell
        Source shell.
    src_path
        Source directory.
    dst_shell
        Destination shell.
    dst_path
        Destination directory.
    run_shell : optional
        Shell where to run rsync. Default is local machine.
    args : list of str, optional
        Additional arguments to rsync. Default is none.

    """
    if (not spur.is_local_shell(src_shell) and not spur.is_local_shell(dst_shell) and
        run_shell is not src_shell and run_shell is not dst_shell):
        raise Exception("rsync cannot work with two remote shells")

    if run_shell is None:
        run_shell = spur.LocalShell()

    ssh_port = 22
    cmd_pass = []
    if spur.is_local_shell(src_shell) or run_shell is src_shell:
        cmd_src = [src_path]
    else:
        ssh_port = src_shell._port
        if src_shell._password is not None:
            cmd_pass = ["sshpass", "-p", src_shell._password]
        cmd_src = ["%s@%s:%s" % (src_shell.username, src_shell.hostname, src_path)]
    if spur.is_local_shell(dst_shell) or run_shell is dst_shell:
        cmd_dst = [dst_path]
    else:
        ssh_port = dst_shell._port
        if dst_shell._password is not None:
            cmd_pass = ["sshpass", "-p", dst_shell._password]
        cmd_dst = ["%s@%s:%s" % (dst_shell.username, dst_shell.hostname, dst_path)]

    cmd = []
    cmd += cmd_pass
    cmd += ["rsync", "-az"]
    cmd += ["-e", "ssh -p %d -o StrictHostKeyChecking=no" % ssh_port]
    cmd += cmd_src
    cmd += cmd_dst
    cmd += args
    run_shell.run(cmd)
