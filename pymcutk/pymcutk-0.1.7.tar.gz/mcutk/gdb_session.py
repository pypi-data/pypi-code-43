import os
import sys
import time
import logging
import tempfile
import subprocess
import pexpect
from pexpect.popen_spawn import PopenSpawn

PY = sys.version_info[0]

try:
  basestring
except NameError:
  basestring = str


class GDBSessionInitFailed(Exception):
    pass


class GDBTimeout(Exception):
    pass


class GDBSession(object):
    """GDB debug session manager. This class will start a gdb process in backend.
    And provide methods allow user interact with gdb or manage the state.

    Example:
        >>> session = GDBSession.start("/path/to/gdb <image.elf> -x <gdb.init>")
        >>> response = session.run_cmd("load)
        >>> response = session.run_cmd("continue", timeout=10)
        >>> response = session.run_cmd("q")
        >>> session.close()
        >>> session.console_output
    """


    @staticmethod
    def start(cmdline):
        """A shortcut to start a gdb session.

        Arguments:
            cmdline {str} -- gdb startup command line.
        """

        session = GDBSession(cmdline)
        session.init()
        return session



    def __init__(self, executable):
        """GDB Session constructor.

        Create a gdb debug session. Pass the gdb executable path (also with arguments) as the
        startup command line.

        Arguments:
            executable {str} -- gdb startup command line or gdb executable.
        """

        self.executable = executable
        self._spawn = None
        self._logfile = None
        self._console = ''
        self.initial_arguments = '-ex "set tcp connect-timeout 100"'



    def init(self):
        """Start GDB process in backend."""

        logging.info(self.executable)
        self._logfile = tempfile.SpooledTemporaryFile(200, mode='w+')
        self._spawn = PopenSpawn(self.executable, logfile=sys.stdout, encoding='utf8', timeout=None)
        self._spawn.logfile_read = self._logfile

        try:
            self._spawn.expect(u'\(gdb\) ')
        except Exception as e:
            raise GDBSessionInitFailed(str(e))



    def run_cmd(self, cmd, timeout=None):
        """Run gdb command.

        Arguments:
            cmd {str} -- gdb command
            timeout {int} -- max timeout to wait the response, default no timeout.

        Returns:
            {str} -- gdb response text
        """
        response = ''

        if timeout is None:
            timeout = -1

        if PY == 2:
            cmd = unicode(cmd, "utf-8")

        try:
            self._spawn.sendline(cmd)
            self._spawn.expect(u'\(gdb\) ', timeout=timeout)

        except pexpect.TIMEOUT:
            raise GDBTimeout('CMD: %s, wait for response timeout!'%cmd)

        except pexpect.EOF:
            logging.debug("GDB EOF")

        if isinstance(self._spawn.before, basestring):
            response = self._spawn.before

        if isinstance(self._spawn.after, basestring):
            response += self._spawn.after

        return response


    def run_cmds(self, cmds):
        """Run a list of commands.
        """

        for cmd in cmds:
            self.run(cmd)


    @property
    def is_alive(self):
        """GDB process is alive or not"""

        return self._spawn.proc.poll() == None



    @property
    def pid(self):
        """GDB process pid"""

        return self._spawn.proc.pid


    def kill(self):
        """Kill GDB process"""

        return slef._spawn.proc.kill()


    @property
    def console_output(self):
        """Return all console output
        You must call this, when session is closed.

        """

        if self.is_alive:
            raise RuntimeError('the console output cannot access when session is alive!')
        return self._console


    def _handle_console_output(self):
        self._logfile.seek(0)
        self._console = self._logfile.read()
        self._logfile.close()


    def close(self):
        """Close session and make sure process has exited."""

        if self.is_alive:
            try:
                # send q command to make sure gdb exit
                self._spawn.logfile = None
                self._spawn.sendline('q')
            except IOError:
                pass
        self._spawn.wait()
        self._handle_console_output()
        logging.info("gdb session is closed!")



    def __enter__(self):
        self.init()
        return self



    def __exit__(self, etype, evalue, tb):
        self.close()
