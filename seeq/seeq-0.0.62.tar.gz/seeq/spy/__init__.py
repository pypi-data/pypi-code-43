"""
Short for Seeq PYthon, the Spy library provides methods to interact with data that is exposed to the Seeq Server.
"""

from . import assets
from . import docs
from . import workbooks

from ._login import login
from ._login import logout
from ._plot import plot
from ._pull import pull
from ._push import push
from ._search import search
from ._common import DEFAULT_WORKBOOK_PATH, Status

__all__ = ['assets', 'docs', 'workbooks', 'login', 'logout', 'plot', 'pull', 'push', 'search',
           'DEFAULT_WORKBOOK_PATH', 'Status']
