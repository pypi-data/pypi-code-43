import os

from .types import Path

__all__ = ["mkdirs_thread_safe", "make_sure_dir_exists"]


def mkdirs_thread_safe(dst: Path) -> None:
    """Make directories leading to 'dst' if they don't exist yet"""
    if dst == "" or os.path.exists(dst):
        return
    head, _ = os.path.split(dst)
    if os.sep == ":" and not ":" in head:
        head = head + ":"
    mkdirs_thread_safe(head)
    try:
        os.mkdir(dst, 0o777)
    except OSError as err:
        if err.errno != 17:  # file exists
            raise


def make_sure_dir_exists(filename: Path) -> None:
    """ Makes sure that the path to file exists, but creating directories. """
    dirname = os.path.dirname(filename)
    # dir == '' for current dir
    if dirname != "" and not os.path.exists(dirname):
        mkdirs_thread_safe(dirname)
