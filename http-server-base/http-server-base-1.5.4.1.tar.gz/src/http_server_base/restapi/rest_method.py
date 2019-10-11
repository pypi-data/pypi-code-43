from typing import Callable

from .extras import CanonicalArgumentListType
from .. import Logged_RequestHandler
from ..tools import RegExpType

class RestMethod:
    name: str
    path: str
    listen_re: RegExpType
    
    query_arguments: CanonicalArgumentListType
    body_arguments: CanonicalArgumentListType
    path_arguments: CanonicalArgumentListType
    header_arguments: CanonicalArgumentListType
    
    action: Callable
    
    def invoke(self, handler:Logged_RequestHandler):
        pass

__all__ = \
[
    'RestMethod',
]
