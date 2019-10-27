import os
import sys
import atexit
import warnings

try:
    import psutil
except:
    psutil = None

from .version import version as __version__


class AlreadyRunningError(Exception):
    """Exception raised when another process is already running with the same pid file."""

    def __init__(self, pid_file_path, other_pid):
        self.pid_file_path = pid_file_path
        self.other_pid = other_pid

    def __str__(self):
        return "Is the server still running with pid %s? If not, then please remove %s file." % (
            self.other_pid, self.pid_file_path)

    def __repr__(self):
        return "%s(%s,%s)" % (self.__class__.__name__, self.pid_file_path, self.other_pid)


def create_pid_file(pid_file_path, silent_abort=False, auto_remove_pid_file=False):
    """Write process id into a pid file and register an atexit function that removes it when the process exits.

    @param pid_file_path: path to the pid file.
    @param silent_abort: Set this flag to silently exit with SystemExit(0) if the server is already running.
    @param auto_remove_pid_file: specify this flag to automatically remove the pid file.
    @return: pid value

    When auto_remove_pid_file is not set and another process is already running with the given pid file, then an
    AlreadyRunning exception is raised.
    """
    #  Must use full path, because atexit may run in a different "current dir"
    pid_file_path = os.path.abspath(pid_file_path)
    if os.path.isfile(pid_file_path):
        pid = open(pid_file_path, "r").read().strip()
        try:
            pid = int(pid)
        except ValueError:
            pid = None
        if pid:
            if psutil is None and auto_remove_pid_file:
                warnings.warn("Automatically removing pid file %s, use this for testing ONLY!" % pid_file_path)
                os.unlink(pid_file_path)
            elif psutil is None or psutil.pid_exists(pid):
                if silent_abort:
                    raise SystemExit(0)
                else:
                    raise AlreadyRunningError(pid_file_path, pid)

    def remove_pid_file():
        if os.path.isfile(pid_file_path):
            os.unlink(pid_file_path)

    atexit.register(remove_pid_file)
    pid = os.getpid()
    with open(pid_file_path, "w+") as pid_file:
        pid_file.write(str(pid))


def create_pid_file_or_exit(pid_file_path, silent_abort=False, auto_remove_pid_file=False, exit_code=2):
    """Pid file handling that is more comfortable to use for the command line.

    Similar to create_pid_file but instead of raising AlreadyRunningError, it prints an error message to stderr
    and raises SystemExit(exit_code)
    """
    try:
        create_pid_file(pid_file_path, silent_abort, auto_remove_pid_file)
    except AlreadyRunningError as e:
        sys.stderr.write(str(e))
        sys.stderr.flush()
        raise SystemExit(exit_code)
