import asyncio

from .protocol import DnsUDP


class Connection:

    def __init__(self, dispatcher_cls, loop, host='0.0.0.0', port=53):
        self.dispatcher_cls = dispatcher_cls
        self.loop = loop
        self.host = host
        self.port = port

    async def start(self):
        print("Starting UDP server")
        transport, protocol = await self.loop.create_datagram_endpoint(
            lambda: DnsUDP(self, self.loop),
            local_addr=('0.0.0.0', 53))
        try:
            await asyncio.sleep(99999999999999)
        finally:
            transport.close()
