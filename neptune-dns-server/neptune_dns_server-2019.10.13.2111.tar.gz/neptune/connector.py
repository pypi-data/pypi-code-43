from neptune import config


class Connector:

    def __init__(self, loop):
        if not hasattr(self, 'connected'):
            self.connected = False
            self.loop = loop
            self.resolve_connectors = []
            self.cache_connector = None
            self.loop.create_task(self.init_connections())

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            instance = super().__new__(cls)
            cls.instance = instance
        return cls.instance

    async def init_connections(self):
        if not self.connected:
            for resolver in config.RESOLVERS:
                setattr(self, resolver, __import__(resolver, globals=globals(), fromlist=['']))
                con = getattr(self, resolver).Connection(loop=self.loop, server_connector=self,
                                                         **getattr(config, resolver.replace('.', '_').upper(), {}))
                self.resolve_connectors.append(con)
            if hasattr(config, 'CACHE'):
                setattr(self, config.CACHE, __import__(config.CACHE, globals=globals()))
                con = getattr(self, config.CACHE).Connection(loop=self.loop,
                                                             **getattr(config, config.CACHE.upper(), {}))
                await con.init_connection()
                self.cache_connector = con
        self.connected = True

    async def resolve(self, name, type, cls):
        for con in self.resolve_connectors:
            result = await con.Resolver.find(type=type,
                                             cls=cls,
                                             name=name)
            if result:
                return result
        return None

    async def cache_set(self, name, type, cls, data, expire):
        assert hasattr(self, 'cache_connector')
        return self.cache_connector.Cache.set(name, type, cls, data, expire)

    async def cache_get(self, name, type, cls):
        assert hasattr(self, 'cache_connector')
        return self.cache_connector.Cache.get(name, type, cls)
