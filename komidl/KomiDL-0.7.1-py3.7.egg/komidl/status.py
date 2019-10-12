# KomiDL - A gallery downloader
# Copyright (C) 2019 DNSheng
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
"""This module contains the StatusBar class

When importing the module, a single instance of StatusBar is created.

Only singletons and public static methods are exported as module-level
functions.
"""

import sys
from contextlib import contextmanager


class StatusBar:
    """A class to draw progress bars and handle user input."""
    # Below is a diagram of terminology used in status bar formatting
    #
    # Constants:                Arguments:
    # ------------------------------------------------------------------
    #   MSG_SIZE = 12      |      msg = 'Progress'   total = 100
    #   BAR = '='          |      length = 21        current = 38
    #
    # Calculations:
    # ------------------------------------------------------------------
    #   bars = 8     precent = 38
    #
    #   MSG        BARS/BAR
    # |<---->|     |<---->|
    # Progress:   [========             ] 38%  <- PERCENT
    # |<-------->| |<----------------->|
    #   MSG_SIZE          LENGTH

    # pylint: disable=invalid-name
    BAR = '='
    MSG_SIZE = 13

    def __init__(self, length: int = 0, total: int = 0):
        self.length = length
        self.total = total
        self.current = 0

    # ==================================================================
    # Context manager instantiators
    # ==================================================================

    @classmethod
    @contextmanager
    def progress(cls,
                 msg: str,
                 length: int,
                 total: int,
                 **kwargs: int
                 ) -> 'StatusBar':
        """Create an instance of StatusBar for drawing progress bars

        Parameters
        ----------
        kwargs['bar']: char         The character to display for progress bars
        kwargs['msg_size']: int     The length of space for msg in progress bar
        """
        sys.stdout.write(f'{msg}\n')
        status_bar = StatusBar(length=length, total=total)
        status_bar.BAR = kwargs.get('bar', status_bar.BAR)
        status_bar.MSG_SIZE = kwargs.get('msg_size', status_bar.MSG_SIZE)
        try:
            yield status_bar
        except Exception as e:
            status_bar.update(status_bar.current, msg="Failed")
            raise e
        else:
            status_bar.update(status_bar.current, msg="Success")
        finally:
            sys.stdout.write('\n')

    # ==================================================================
    # Functionality
    # ==================================================================

    @staticmethod
    def _bar_size(length: int, current: int, total: int) -> int:
        """Return the number of bars to draw"""
        return int((current*length)/float(total))

    @staticmethod
    def _percent(current: int, total: int) -> int:
        """Return the percentage progress"""
        return int(current*100/float(total))

    @staticmethod
    def _carriage_print(line: str) -> None:
        """Print to the current line using a carriage return"""
        sys.stdout.write('\r')
        sys.stdout.write(line)
        sys.stdout.flush()

    def _progress_print(self, msg: str) -> None:
        """Print the progress bar"""
        # Calculate number of bars and percentage progress
        bars = self._bar_size(self.length, self.current, self.total)
        percent = self._percent(self.current, self.total)

        # Format string vars
        bar_str = self.BAR*bars
        msg += ':'

        line = f'{msg:<{self.MSG_SIZE}}[{bar_str:<{self.length}}]{percent:>4}%'
        self._carriage_print(line)

    def update(self, current: int, msg: str = 'Progress') -> None:
        """Update the progress bar with the new current value"""
        if current > self.total:
            raise ValueError(f'Current value ({current}) exceeds total ' +
                             f'({self.total})')
        if current < self.current:
            raise ValueError(f'Current value ({current}) lower than ' +
                             f'historical ({self.current})')

        self.current = current
        self._progress_print(msg)

    # ==================================================================
    # Public static methods
    # ==================================================================

    @staticmethod
    def prompt(msg: str, skip: bool = False) -> bool:
        """Print a yes/no prompt message, returns True if user answered yes"""
        if skip:
            return skip
        response = input(f'{msg} [y/N] ')
        return response.lower() == 'y'


# pylint: disable=invalid-name, protected-access
_statusbar = StatusBar()
progress = _statusbar.progress
prompt = _statusbar.prompt

# Export these for testing
_percent = StatusBar._percent
_bar_size = StatusBar._bar_size
