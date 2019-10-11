from abc import ABC

from tornado.web import RequestHandler

from .irespondable import IRespondable
from .iloggable import ILoggable

class ILogged_RequestHandler(RequestHandler, IRespondable, ILoggable, ABC):
    
    def get_body_or_query_argument(self, name, default=None, strip=True):
        pass
    def get_body_or_query_arguments(self, name, strip=True):
        pass

__all__ = \
[
    'ILogged_RequestHandler',
]
