from conlog import Conlog

import inspect
from itertools import repeat

from .TimeTools import Timetools
from colored import fore, back, style

MAIN_IMPL = True
MODULE_IMPL = True

console = Conlog(__name__,  Conlog.DEBUG, enabled=MODULE_IMPL)


def test_factory():
    ## Factory function

