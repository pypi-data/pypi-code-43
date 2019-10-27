import random
import socket
from ipaddress import IPv4Address

from saturn.protocol.server_tcp import TcpServer
from saturn.socks import reply
from .base import SocksRequest


class SocksRequestBind(SocksRequest):
    action_id = 2

    async def go(self):
        port = random.randrange(30000, 65535)

        new_server = TcpServer(self.dispatcher, self.dispatcher.loop).start_server(port)
        return reply.Success(IPv4Address(socket.gethostbyname(socket.gethostname())), port)
