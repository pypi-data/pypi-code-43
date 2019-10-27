import logging
import socket
from ipaddress import IPv4Address
from ipaddress import ip_network

from saturn import state, config
from saturn.protocol import TcpClient
from saturn.socks import reply
from .base import SocksRequest


class SocksRequestConnect(SocksRequest):
    action_id = 1

    async def go(self):
        assert not isinstance(self.dispatcher.state, state.Connected)
        on_connect = self.dispatcher.loop.create_future()
        allowed_to = False
        for addr in getattr(config, 'ALLOWED_DESTINATIONS', [ip_network('0.0.0.0/0')]):
            if self.dst_addr in ip_network(addr):
                allowed_to = True
                break
        if not allowed_to:
            return reply.ConnectionNotAllowed()
        try:
            self.dispatcher.client_transport, self.client_protocol = await self.dispatcher.loop.create_connection(
                lambda: TcpClient(self.dispatcher, on_connect),
                str(self.dst_addr), self.dst_port)
        except OSError as e:
            if e.errno == 110:
                return reply.NetworkUnreachable()
            if e.errno == 111:
                return reply.ConnectionRefused()
            if e.errno == 113 or e.errno == 101:
                return reply.HostUnreachable()
            if e.errno == 22:
                return reply.AddressTypeNotSupported()
            logging.error(f'TCP Client got {e.errno}: {e} while trying to connect to {self.dst_addr}')
            return reply.Failure()
        self.dispatcher.connected = True
        await on_connect
        self.dispatcher.state = state.Connected()
        return reply.Success(IPv4Address(socket.gethostbyname(socket.gethostname())), 8081)
