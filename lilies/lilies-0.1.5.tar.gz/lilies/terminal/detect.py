import os
import sys
import platform
import subprocess
from builtins import object

from .nocolor import NoColorTerminal
from .ansi8 import Ansi8Terminal
from .ansi8open import Ansi8OpenTerminal
from .aixterm import AixTerminal
from .ansi16 import Ansi16Terminal
from .ansi256 import Ansi256Terminal
from .truecolor import TrueColorTerminal
from .windows import WinTrueColor, Win256Color, WinLegacy


# Note: The order, names, and numbers
# on these may change at any time.
# Do not rely on them long-term.
NO_COLOR = 1
ANSI8 = 2
ANSI8_OPEN = 3
ANSI16 = 4
AIXTERM = 5
ANSI256 = 6
FULL_RGB = 7
WIN10_24BIT = 8
WIN10_256 = 9
WIN32 = 10

TERM_CLASSES = {
    NO_COLOR: NoColorTerminal,
    ANSI8: Ansi8Terminal,
    ANSI8_OPEN: Ansi8OpenTerminal,
    ANSI16: Ansi16Terminal,
    AIXTERM: AixTerminal,
    ANSI256: Ansi256Terminal,
    FULL_RGB: TrueColorTerminal,
    WIN10_24BIT: WinTrueColor,
    WIN10_256: Win256Color,
    WIN32: WinLegacy,
}


_term = None


class SystemProperties(object):
    def __init__(
        self,
        pltform="",
        env={},
        stdout=None,
        version=["0", "0", "0"],
        tput_colors=None,
    ):
        self.platform = pltform
        self.env = env
        self.stdout = stdout
        self.ver = version
        self.tput_colors = tput_colors


def detect_terminal():
    global _term
    if _term is not None:
        return _term

    term_type = _detect()
    term_cls = TERM_CLASSES.get(term_type) or NoColorTerminal
    _term = term_cls()
    return _term


def _get_system():
    plat = platform.system()
    env = os.environ
    stdout = sys.stdout
    if "Windows" in plat:
        version = platform.version().split(".")
    else:
        version = platform.release().split(".")
    try:
        result = subprocess.check_output(["tput", "colors"])
        tput_colors = int(result.strip())
    except Exception:
        tput_colors = None

    return SystemProperties(plat, env, stdout, version, tput_colors)


def print_features(system=_get_system()):
    print("Platform: {}".format(system.platform))
    print("Version: {}".format(system.ver))
    print("isatty: {}".format(system.stdout.isatty()))
    print("NOCOLOR: {}".format(system.env.get("NO_COLOR") is not None))
    print("TERM: {}".format(system.env.get("TERM")))
    print("TERM_PROGRAM: {}".format(system.env.get("TERM_PROGRAM")))
    print("COLORTERM: {}".format(system.env.get("COLORTERM")))
    print("TPut Colors: {}".format(system.tput_colors))


def _detect(system=_get_system()):
    if not system.stdout.isatty() or system.env.get("NO_COLOR") is not None:
        return NO_COLOR

    # Check colorterm env for modern
    # terminal settings
    colorterm = system.env.get("COLORTERM")
    if colorterm:
        if colorterm in {"truecolor", "24bit"}:
            return FULL_RGB
        if colorterm in {"8bit"}:
            return ANSI256

    termprogram = system.env.get("TERM_PROGRAM")
    if termprogram:
        if termprogram in {"iTerm.app", "Hyper"}:
            return FULL_RGB
        if termprogram in {"Apple_Terminal"}:
            return ANSI256

    if "CYGWIN" in system.platform:
        return _get_cygwin_color(system)

    term = system.env.get("TERM")
    if term:
        if "screen-256" in term or "xterm-256" in term:
            return ANSI256
        if "vt100" in term:
            return ANSI16
        if term in {"screen", "xterm", "color", "ansi", "linux"}:
            return ANSI8_OPEN

    if "Windows" in system.platform:
        return _get_windows_color(system)

    if term:
        if "aixterm" in term or "xterm-16" in term:
            return AIXTERM

        if term in {"dumb"}:
            return NO_COLOR

    termcolors = _get_termcolors(system.tput_colors)
    if termcolors:
        return termcolors

    # fuck it, most terms should be 8 color...
    return ANSI8


def _get_cygwin_color(system):
    # Cygwin takes over the system platform variable.
    # It's hard to determine the exact version that
    # 24-bit color was introduced, but anyone with a
    # version older than 2.9 should update...
    try:
        version_major = int(system.ver[0])
        version_minor = int(system.ver[1])
        if version_major >= 3:
            return FULL_RGB
        if version_major == 2 and version_minor >= 9:
            return FULL_RGB
    except Exception:
        pass
    return AIXTERM


def _get_windows_color(system):
    term = system.env.get("TERM")
    mingw = system.env.get("MINGW64")

    # detects git bash, which needs colorama.
    if term and "cygwin" in term and mingw and "MSYSTEM" in mingw:
        return WIN32

    release = system.ver
    if release[0] == "10":
        # Windows10 started to add real color support.
        # Detect if this version is up to date
        micro_ver = int(release[2])
        if micro_ver > 10586:
            return WIN10_24BIT if micro_ver > 14931 else WIN10_256

    return WIN32


def _get_termcolors(tput_colors):
    if tput_colors is None:
        return None
    if tput_colors >= 256:
        # Honestly, if this is more than 256,
        # we can't be sure if it's truecolor.
        # There are some weird terminals out there,
        # including 4352 color support?
        return ANSI256
    if tput_colors >= 16:
        # sadly I can't be certain that this will
        # properly support bright colors?
        return ANSI8_OPEN
    if tput_colors >= 8:
        return ANSI8
    return NO_COLOR
