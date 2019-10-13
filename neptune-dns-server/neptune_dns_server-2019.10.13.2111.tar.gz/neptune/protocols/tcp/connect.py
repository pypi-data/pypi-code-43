import asyncio

from .protocol import DnsTCP


class Connection:

    def __init__(self, dispatcher_cls, loop, host='0.0.0.0', port=53):
        self.dispatcher_cls = dispatcher_cls
        self.loop = loop
        self.host = host
        self.port = port

    async def start(self):
        # Get a reference to the event loop as we plan to use
        # low-level APIs.

        server = await self.loop.create_server(
            lambda: DnsTCP(self, self.loop),
            self.host, self.port)

        async with server:
            await server.serve_forever()
