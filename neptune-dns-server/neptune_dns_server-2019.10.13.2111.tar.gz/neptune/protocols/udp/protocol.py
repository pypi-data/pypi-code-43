import asyncio
from typing import Union, Text, Tuple


class DnsUDP(asyncio.DatagramProtocol):

    def __init__(self, connection, loop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.connection = connection

    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        self.transport = transport

    def datagram_received(self, data: Union[bytes, Text], addr: Tuple[str, int]) -> None:
        dispatcher = self.connection.dispatcher_cls(self.loop)
        task = asyncio.Task(self.to_async(dispatcher, data, addr))

    @asyncio.coroutine
    def to_async(self, dispatcher, data, addr):
        result_data = yield from dispatcher.handle(data)
        self.transport.sendto(result_data, addr)

