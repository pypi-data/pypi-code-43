from .grow import grow
from .cli_utils import columnify, sortify, bordered
from .base_utils import isstringish, islilyblock, wilt
from .manage import lilies_init
from .lilystring import LilyString
from .lilyblock import LilyBlock, block
from . import terminal

__version__ = "0.0.4"

version = VERSION = __version__


def print_test():
    term = terminal.detect_terminal()
    term.test()


lilies_init()

__all__ = [
    # helpers
    "grow",
    "wilt",
    "block",
    "isstringish",
    "islilyblock",
    # layouts
    "columnify",
    "sortify",
    "bordered",
    # classes
    "LilyString",
    "LilyBlock",
]
