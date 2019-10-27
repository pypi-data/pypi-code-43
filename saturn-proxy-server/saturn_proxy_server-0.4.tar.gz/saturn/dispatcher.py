from saturn import state
from saturn.socks import SocksHello, SocksAuthenticate
from saturn.socks.request import SocksRequest


class Dispatcher:
    def __init__(self, server, loop, transport):
        self.server_transport = transport
        self.server = server
        self.loop = loop
        self.client_transport = None
        self.state = state.NotAuthenticated()
        self.busy = False
        self.previous = None

    async def handle(self, data):
        result = None
        if isinstance(self.state, state.Connected):
            self.client_transport.write(data)
        elif isinstance(self.state, state.NotAuthenticated):
            result = SocksHello(self, data).reply()
        elif isinstance(self.state, state.WaitingAuthenticationData):
            result = await SocksAuthenticate(self, data).authenticate()
        elif isinstance(self.state, state.Authenticated):
            request = SocksRequest.parse(self, data)
            result = await request.go()
        return result

    def reply(self, data):
        self.server_transport.write(data)
