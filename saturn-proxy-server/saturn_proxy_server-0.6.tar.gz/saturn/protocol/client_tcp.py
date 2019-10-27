import asyncio


class TcpClient(asyncio.Protocol):
    def __init__(self, dispatcher, on_connect):
        self.dispatcher = dispatcher
        self.on_connect = on_connect

    def connection_made(self, transport):
        self.transport = transport
        self.on_connect.set_result(True)

    def data_received(self, data):
        self.dispatcher.reply(data)

    def connection_lost(self, exc):
        self.dispatcher.server_transport.close()

    def send(self, data):
        self.transport.write(data)
