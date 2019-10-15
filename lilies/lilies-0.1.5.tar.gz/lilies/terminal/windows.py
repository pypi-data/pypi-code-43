from .win10mixin import Win10Mixin
from .win32mixin import Win32Mixin
from .truecolor import TrueColorTerminal
from .ansi256 import Ansi256Terminal
from .aixterm import AixTerminal


class WinTrueColor(Win10Mixin, TrueColorTerminal):
    pass


class Win256Color(Win10Mixin, Ansi256Terminal):
    pass


class WinLegacy(Win32Mixin, AixTerminal):
    pass
