from .resolver import Resolver
from .local_cache import Cache


class Connection:

    def __init__(self, loop, server_connector):
        self.loop = loop
        self.server_connector = server_connector
        self.Resolver = Resolver(self)
        self.Cache = Cache(self.loop)
