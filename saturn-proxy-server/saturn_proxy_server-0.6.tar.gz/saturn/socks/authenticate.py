from saturn import state


class SocksAuthenticate:
    def __init__(self, dispatcher, data):
        self.data = data
        self.dispatcher = dispatcher
        self.server = dispatcher.server

    async def authenticate(self):
        if await self.server.auth(self.dispatcher.state.method, self.data):
            self.dispatcher.state = state.Authenticated()
            return int(1).to_bytes(1, byteorder='big') + int(0).to_bytes(1, byteorder='big')
        return int(1).to_bytes(1, byteorder='big') + int(10).to_bytes(1, byteorder='big')
