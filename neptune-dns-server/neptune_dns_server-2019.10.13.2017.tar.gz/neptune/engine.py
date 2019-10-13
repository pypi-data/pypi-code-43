from neptune import config
from neptune.protocols.dispatcher import Dispatcher


class Server:
    def __init__(self, loop):
        self.loop = loop
        self.protocols = []

    def load_protocols(self):
        for proto in config.PROTOCOLS:
            _proto = __import__(proto, fromlist=[''])
            con = _proto.Connection(**{**getattr(config, proto.replace('.', '_').upper()),
                                       'loop': self.loop, 'dispatcher_cls': Dispatcher})
            self.protocols.append(con)

    async def start(self):
        self.load_protocols()
        for proto in self.protocols:
            self.loop.create_task(proto.start())


if __name__ == '__main__':
    server = Server(config.loop)
    config.loop.run_until_complete(server.start())
    config.loop.run_forever()
