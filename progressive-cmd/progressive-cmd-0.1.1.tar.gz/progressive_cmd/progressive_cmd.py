import subprocess
from contextlib import suppress
from typing import Any, Set, TextIO

from progressive_cmd import text


class ProgressiveCmd:
    """Executes a cmd while interpreting its completion percentage.

    The completion percentage of the cmd is stored in
    :attr:`.percentage` and the user can obtain percentage
    increments by executing :meth:`.increment` or by passing
    a *callback* when initializing.

    This class is useful to use within a child thread, so a main
    thread can request from time to time the percentage / increment
    status of the running command.
    """
    READ_LINE = None
    DECIMALS = {4, 5, 6}
    """Number of digits a decimal number can have."""
    DECIMAL_NUMBERS = 2
    """Number of decimal digits (after the comma) a number can have."""
    INT = {1, 2, 3}
    """Number of digits an integer number can have."""

    def __init__(self, *cmd: Any,
                 stdout=subprocess.DEVNULL,
                 digits: Set[int] = INT,
                 decimal_digits: int = None,
                 read: int = READ_LINE,
                 callback=None,
                 check=True):
        """
        Initializes ProgressiveCMD.

        :param cmd: The command to execute.
                    This is converted to a tuple of strings and
                    passed-in to :class:`subprocess.Popen`
        :param stderr: the stderr passed-in to :class:`subprocess.Popen`.
        :param stdout: the stdout passed-in to :class:`subprocess.Popen`.
        :param digits: The number of chars the cmd uses to represent
                       a percentage. A set of ``{4,5,6}`` means that
                       the percentage can have 4, 5, or 6 digits,
                       including the decimal punctuation (period,
                       comma).
                       Usual cases are :attr:`.DECIMALS` and,
                       by default, :attr:`.INT`.
        :param read: For commands that do not print lines, how many
                     characters we should read between updates.
                     The percentage should be between those
                     characters. This does not to be exact, but a guess.
                     A big number will take more time to update,
                     and a small number will have more chance to break
                     the percentage between lectures, loosing updates.
                     If the program updates constantly, just write
                     an educated guess and it will just work fine,
                     although you might loose an update from time to
                     time. By default, it reads full lines .
        :param callback: If passed in, this method is executed every time
                         run gets an update from the command, passing
                         in the increment from the last execution.
                         If not passed-in, you can get such increment
                         by executing manually the ``increment`` method.
                         Callback receives two arguments:
                         A float with the percentage increment since
                         the last callback was executed.
                         A float with the total percentage.
        :param check: Raise error if subprocess return code is non-zero.
        """
        self.cmd = tuple(str(c) for c in cmd)
        self.read = read
        self.step = 0
        self.check = check
        self.number_chars = digits
        self.decimal_numbers = decimal_digits
        # We call subprocess in the main thread so the main thread
        # can react on ``CalledProcessError`` exceptions
        self.conn = conn = subprocess.Popen(self.cmd,
                                            universal_newlines=True,
                                            stderr=subprocess.PIPE,
                                            stdout=stdout)
        self.out: TextIO = conn.stdout if stdout == subprocess.PIPE else conn.stderr
        self.callback = callback
        self._last_update_percentage = 0
        self.percentage = 0

    @property
    def percentage(self):
        return self._percentage

    @percentage.setter
    def percentage(self, v):
        self._percentage = v
        if self.callback and self._percentage > 0:
            increment = self.increment()
            if increment > 0:  # Do not bother calling if there has not been any increment
                self.callback(increment, self._percentage)

    def run(self) -> None:
        """Processes the output."""
        while True:
            out = self.out.read(self.read) if self.read else self.out.readline()
            if out:
                with suppress(StopIteration):
                    self.percentage = next(
                        text.positive_percentages(out, self.number_chars, self.decimal_numbers)
                    )
            else:  # No more output
                break
        return_code = self.conn.wait()  # wait until cmd ends
        if self.check and return_code != 0:
            raise subprocess.CalledProcessError(self.conn.returncode,
                                                self.conn.args,
                                                stderr=self.conn.stderr.read())

    def increment(self):
        """Returns the increment of progression from
        the last time this method is executed.
        """
        # Some cmds' increment can be negative at one point
        # so we prefer to loose this update (i.e. be 0)
        increment = max(self.percentage - self._last_update_percentage, 0)
        self._last_update_percentage = self.percentage
        return increment
