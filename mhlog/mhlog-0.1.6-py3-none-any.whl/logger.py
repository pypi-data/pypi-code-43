import io
import sys

from datetime import datetime
from pathlib import Path

class Logger:

    _time_format = '%Y-%m-%d %H:%M:%S'
    _file_mode   = 0o664

    def __init__(self, app_name: str):
        self._app_name = app_name
        self._level    = self.INFO
        self._l2std    = True
        self._l2file   = False
        self._fname    = Path.home() / Path('.logs/%s.log' % app_name)

    # -------------------------------------------------------------------------
    # Public interface

    # Output

    @property
    def log_to_std(self) -> bool:
        return self._l2std

    @log_to_std.setter
    def log_to_std(self, val) -> None:
        if val:
            self._l2std = True
        else:
            self._l2std = False

    @property
    def log_to_file(self) -> bool:
        return self._l2file

    @log_to_file.setter
    def log_to_file(self, val) -> None:
        if val:
            self._l2file = True
            self._fname.parent.mkdir(parents=True, exist_ok=True)
            self._fname.touch(mode=self._file_mode)
        else:
            self._l2file = False

    # Logging level

    @property 
    def FATAL(self) -> int:
        return 6

    @property 
    def ERROR(self) -> int:
        return 5

    @property 
    def WARNING(self) -> int:
        return 4

    @property 
    def IMPORTANT(self) -> int:
        return 3

    @property 
    def INFO(self) -> int:
        return 2

    @property 
    def DEBUG(self) -> int:
        return 1

    @property 
    def TRACE(self) -> int:
        return 0

    @property
    def level(self) -> str:
        return self._level

    @level.setter
    def level(self, lvl: int) -> None:
        self._level = lvl

    # Logging methods

    def fatal(self, *args, sep: str = ' ', ecode: int = 1):
        '''
        Log a fatal event and exit.
        :param ecode: Error code
        '''
        if self._level <= self.FATAL:
            if self._l2std:
                self._log(*args, sep=sep, symbol='!!', file=sys.stderr)
            if self._l2file:
                with self._fname.open('a') as f:
                    self._log(*args, sep=sep, symbol='!!', file=f)
        sys.exit(ecode)

    def error(self, *args, sep=' '):
        '''Log an error.'''
        if self._level <= self.ERROR:
            if self._l2std:
                self._log(*args, sep=sep, symbol='!', file=sys.stderr)
            if self._l2file:
                with self._fname.open('a') as f:
                    self._log(*args, sep=sep, symbol='!', file=f)

    def warning(self, *args, sep=' '):
        '''Log a warning.'''
        if self._level <= self.WARNING:
            if self._l2std:
                self._log(*args, sep=sep, symbol='-', file=sys.stderr)
            if self._l2file:
                with self._fname.open('a') as f:
                    self._log(*args, sep=sep, symbol='-', file=f)

    def important(self, *args, sep=' '):
        if self._level <= self.IMPORTANT:
            if self._l2std:
                self._log(*args, sep=sep, symbol='*', file=sys.stdout)
            if self._l2file:
                with self._fname.open('a') as f:
                    self._log(*args, sep=sep, symbol='*', file=f)

    def info(self, *args, sep=' '):
        if self._level <= self.INFO:
            if self._l2std:
                self._log(*args, sep=sep, symbol=' ', file=sys.stdout)
            if self._l2file:
                with self._fname.open('a') as f:
                    self._log(*args, sep=sep, symbol=' ', file=f)

    def debug(self, *args, sep=' '):
        if self._level <= self.DEBUG:
            if self._l2std:
                self._log(*args, sep=sep, symbol='~', file=sys.stdout)
            if self._l2file:
                with self._fname.open('a') as f:
                    self._log(*args, sep=sep, symbol='~', file=f)

    def trace(self, *args, sep=' '):
        if self._level <= self.TRACE:
            if self._l2std:
                self._log(*args, sep=sep, symbol='.', file=sys.stdout)
            if self._l2file:
                with self._fname.open('a') as f:
                    self._log(*args, sep=sep, symbol='.', file=f)

    # -------------------------------------------------------------------------
    # Private members

    # Logging printing helpers

    def _log(self, *args, sep: str, symbol: str, file: io.IOBase) -> None:
        msg = sep.join([itm.__str__() for itm in args])
        prefix = '[%s] %s:' % (symbol, datetime.now().strftime(self._time_format))
        pre_nl = '[/]'
        for (i, line) in enumerate(msg.split(sep='\n')):
            if i == 0:
                print(prefix, line, file=file)
            else:
                print(pre_nl, line, sep='\t', file=file)
