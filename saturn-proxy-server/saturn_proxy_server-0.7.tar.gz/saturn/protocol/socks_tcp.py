import asyncio

from saturn.dispatcher import Dispatcher


class Socks5TcpServer(asyncio.Protocol):

    def __init__(self, server, loop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.server = server

    def connection_made(self, transport):
        self.transport = transport
        self.dispatcher = Dispatcher(self.server, self.loop, self.transport)

    def data_received(self, data):
        asyncio.Task(self.async_data_handler(data))

    def connection_lost(self, exc) -> None:
        self.transport.close()

    @asyncio.coroutine
    def async_data_handler(self, data: bytes) -> None:
        reply = yield from self.dispatcher.handle(data)
        if reply:
            self.transport.write(bytes(reply))
        else:
            return

    async def start_server(self, host='0.0.0.0', port=8080):
        server = await self.loop.create_server(
            lambda: Socks5TcpServer(self.server, self.loop), host, port)
        async with server:
            await server.serve_forever()


async def main(server, loop):
    server = await loop.create_server(
        lambda: Socks5TcpServer(server, loop), host='0.0.0.0', port=8082)
    async with server:
        await server.serve_forever()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main(loop))
