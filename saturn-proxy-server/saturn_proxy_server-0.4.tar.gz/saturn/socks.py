import random
import socket
from ipaddress import IPv4Address

from saturn import protocol
from saturn import state
from saturn.protocol.client_tcp import TcpClient


class SocksHello(SocksPacket):
    def __init__(self, dispatcher, data):
        super().__init__(data)
        self.dispatcher = dispatcher
        self.nmethods = data[1]
        self.methods = [x for x in data[2:2 + self.nmethods]]

    def reply(self):
        for m in self.dispatcher.server.server_auth_methods:
            if m in self.methods:
                self.dispatcher.state = state.WaitingAuthenticationData(
                    method=m) if not m == 0 else state.Authenticated()
                return self.ver.to_bytes(1, byteorder='big') + int.to_bytes(m, 1, byteorder='big')
        return self.ver.to_bytes(1, byteorder='big') + int.to_bytes(255, 1, byteorder='big')


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


class SocksRequestBind(SocksRequest):

    def __init__(self, dispatcher, data):
        assert len(data) >= 10
        super().__init__(dispatcher, data)

    async def go(self):
        on_connect = self.dispatcher.loop.create_future()
        try:
            self.dispatcher.client_transport, self.client_protocol = await self.dispatcher.loop.create_connection(
                lambda: TcpClient(self.dispatcher, on_connect),
                str(self.dst_addr), self.dst_port)
        except OSError as e:
            print(e.errno, e)
        try:
            port = random.randrange(30000, 65535)
            self.dispatcher.loop.create_task(
                protocol.TcpServer(self, self.dispatcher.loop).start_server(self.host, port))
        except OSError as e:
            print(e.errno, e)
        return SocksTcpReply(self.dispatcher, 5, 0, 0, 1, int(IPv4Address(socket.gethostbyname(socket.gethostname()))),
                             port)


class SocksRequestUdpAssociate(SocksRequest):
    async def go(self):
        print('wooops2')
