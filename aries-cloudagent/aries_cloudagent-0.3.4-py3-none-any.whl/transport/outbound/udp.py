"""UDP outbound transport."""

import asyncio
import logging
from socket import AF_INET, SOCK_DGRAM, IPPROTO_IP
from urllib.parse import urlparse

from ...messaging.outbound_message import OutboundMessage

from .base import BaseOutboundTransport

LOGGER = logging.getLogger(__name__)

IP_MTU = 14
IP_MTU_DISCOVER = 10
IP_PMTUDISC_DONT = 0  # Never send DF frames.
IP_PMTUDISC_WANT = 1  # Use per route hints.
IP_PMTUDISC_DO = 2  # Always DF.
IP_PMTUDISC_PROBE = 3  # Ignore dst pmtu.


class UdpProtocol(asyncio.DatagramProtocol):
    """Protocol instance for handling a single UDP connection."""

    def __init__(
        self, server: "UdpTransport", loop: asyncio.AbstractEventLoop, mtu: int = None
    ):
        """Instantiate the protocol instance."""
        self.addr: str = None
        self.loop: asyncio.AbstractEventLoop = loop
        self.transport: asyncio.DatagramTransport
        self.server = server
        self.laddr = None
        self.raddr = None

    def connection_made(self, transport: asyncio.DatagramTransport):
        """Handle the opening of the connection."""
        self.transport = transport
        print("ob conn made")
        socket = self.transport.get_extra_info("socket")
        socket.setsockopt(IPPROTO_IP, IP_MTU_DISCOVER, IP_PMTUDISC_WANT)
        print("MTU:", socket.getsockopt(IPPROTO_IP, IP_MTU))

    def connection_lost(self, exc):
        """Handle the connection being closed."""
        self.transport = None
        LOGGER.info("UDP outbound connection closed")
        print("ob conn lost")

    async def send(self, result: bytes):
        """Send a message to the socket connection."""
        if self.transport:
            print(f"send message {len(result)}")
            self.transport.sendto(result, self.laddr)
        else:
            LOGGER.error("UDP message dropped, no connection")

    def datagram_received(self, data: bytes, addr: str):
        """Handle a received UDP message."""
        # TODO - pass back to UdpTransport, then to conductor
        print(f"received data {addr}")
        # pass

    def error_received(self, exc):
        """Handle an error on the UDP connection."""
        LOGGER.exception("UDP outbound transport error:")


class UdpTransport(BaseOutboundTransport):
    """UDP outbound transport class."""

    schemes = ("udp",)

    def __init__(self) -> None:
        """Initialize an `UdpTransport` instance."""
        super(UdpTransport, self).__init__()
        self.transport: asyncio.DatagramTransport

    async def start(self):
        """Start the transport."""

    async def stop(self):
        """Stop the transport."""
        # would close any pending connections here

    async def handle_message(self, message: OutboundMessage):
        """
        Handle message from queue.

        Args:
            message: `OutboundMessage` to send over transport implementation
        """
        print("received outbound")
        try:
            # https://blog.powerdns.com/2012/10/08/on-binding-datagram-udp-sockets-to-the-any-addresses/

            url = urlparse(message.endpoint)
            loop: asyncio.BaseEventLoop = asyncio.get_event_loop()
            addr = await loop.getaddrinfo(
                url.hostname, url.port, family=AF_INET, type=SOCK_DGRAM
            )
            for i in addr:
                print(i)
            try:
                transport, protocol = await loop.create_datagram_endpoint(
                    lambda: UdpProtocol(self, loop),
                    remote_addr=(url.hostname, url.port),
                    # IPv6 currently only supported in Docker when on Linux
                    # and specifically enabled
                    family=AF_INET,
                )
            except OSError:
                LOGGER.exception("Error creating outbound UDP endpoint:")
                raise
        except:
            LOGGER.exception("Error creating outbound UDP endpoint:")
            raise
        print(f"created endpoint {url.hostname} {url.port}")
        payload = message.payload
        payload = "-" * 1500
        if isinstance(payload, str):
            payload = payload.encode("utf-8")
        await protocol.send(payload)
        # await asyncio.sleep(2)
        print("sent message")
        # transport.close()
        # print("closed transport")
