from .grow import grow
from .cli_utils import columnify, sortify, bordered
from .base_utils import isstringish, islilyblock, wilt
from .manage import lilies_init
from .lilystring import LilyString
from .lilyblock import LilyBlock, block
from . import compiler

__version__ = "0.1.4"

version = VERSION = __version__


def print_test():
    term = compiler.get_compiler().term
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
