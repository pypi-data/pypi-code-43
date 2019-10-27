import asyncio
from ipaddress import IPv4Address



class TcpServer(asyncio.Protocol):
    def __init__(self, dispatcher, loop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.dispatcher = dispatcher

    def connection_made(self, transport):
        from saturn.socks import reply
        self.transport = transport
        addr = IPv4Address(self.transport.get_extra_info('peername')[0])
        port = self.transport.get_extra_info('peername')[1]
        self.dispatcher.server_transport.write(reply.Success(addr, port))

    def data_received(self, data: bytes) -> None:
        self.dispatcher.client_transport.write(data)

    async def start_server(self, host='0.0.0.0', port=8080):
        server = await self.loop.create_server(
            lambda: TcpServer(self.dispatcher, self.loop), host, port)
        async with server:
            await server.serve_forever()
