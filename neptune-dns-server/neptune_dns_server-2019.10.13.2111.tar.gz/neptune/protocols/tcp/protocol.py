import asyncio
from typing import Union, Text, Tuple


class DnsTCP(asyncio.Protocol):

    def __init__(self, connection, loop, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.loop = loop
        self.connection = connection

    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        self.transport = transport

    def data_received(self, data: Union[bytes, Text]) -> None:
        dispatcher = self.connection.dispatcher_cls(self.loop, self, self.transport.get_extra_info('peername'))
        task = asyncio.Task(self.to_async(dispatcher, data))

    @asyncio.coroutine
    def to_async(self, dispatcher, data):
        result_data = yield from dispatcher.handle(data)
        self.transport.write(result_data)

