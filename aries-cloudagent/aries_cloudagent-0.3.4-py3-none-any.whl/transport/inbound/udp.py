"""UDP Transport classes and functions."""

import asyncio
import logging
from typing import Coroutine

from ...messaging.socket import SocketRef

from .base import BaseInboundTransport, InboundTransportSetupError

LOGGER = logging.getLogger(__name__)


class UdpProtocol(asyncio.DatagramProtocol):
    """Protocol instance for handling a single UDP connection."""

    def __init__(self, server: "UdpTransport", loop: asyncio.AbstractEventLoop):
        """Instantiate the protocol instance."""
        self.addr: str = None
        self.loop: asyncio.AbstractEventLoop = loop
        self.register: Coroutine
        self.server = server
        self.socket_ref: SocketRef
        self.transport: asyncio.DatagramTransport

    def connection_made(self, transport: asyncio.DatagramTransport):
        """Handle the opening of the connection."""
        print("inbound conn made")
        self.transport = transport
        self.register: asyncio.Task = self.loop.create_task(
            self.server.register_socket(handler=self.send)
        )
        self.register.add_done_callback(self.receive_socket_ref)

    def receive_socket_ref(self, fut: asyncio.Future):
        """Receive the socket ref from the server."""
        print("inbound socket ok")
        socket_ref: SocketRef = fut.result()
        if self.transport:
            self.socket_ref = socket_ref
        else:
            # too late
            self.loop.create_task(socket_ref.close())

    @property
    def socket_ref_id(self) -> str:
        """Accessor for the socket ref ID."""
        return self.socket_ref and self.socket_ref.socket_id

    def connection_lost(self, exc):
        """Handle the connection being closed."""
        print("inbound conn lost")
        if self.socket_ref:
            self.loop.create_task(self.socket_ref.close())
            self.socket_ref = None
        self.transport = None
        LOGGER.info("UDP inbound connection closed")

    async def send(self, result: bytes):
        """Send a message back to the socket connection.

        NOTE: Since we're not using DTLS this address is unverified
        and could end up spamming a third party.
        """
        print("inbound send result")
        if self.transport:
            self.transport.sendto(result)
        else:
            # FIXME: raise exception here?
            LOGGER.info("UDP response dropped, connection lost")

    def datagram_received(self, data: bytes, addr: str):
        """Handle a received UDP message."""
        print("inbound got data")
        self.loop.create_task(self.server.inbound_message_handler(data, addr, self))

    def error_received(exc):
        """Handle an error on the UDP connection."""
        LOGGER.exception("UDP inbound transport error")


class UdpTransport(BaseInboundTransport):
    """UDP Transport class."""

    def __init__(
        self,
        host: str,
        port: int,
        message_router: Coroutine,
        register_socket: Coroutine,
    ) -> None:
        """
        Initialize a Transport instance.

        Args:
            host: Host to listen on
            port: Port to listen on
            message_router: Function to pass incoming messages to
            register_socket: A coroutine for registering a new socket

        """
        self.host = host
        self.port = port
        self.message_router = message_router
        self.register_socket = register_socket
        self.transport = None

        self._scheme = "udp"

    @property
    def scheme(self):
        """Accessor for this transport's scheme."""
        return self._scheme

    async def start(self) -> None:
        """
        Start this transport.

        Raises:
            InboundTransportSetupError: If there was an error starting the webserver

        """
        loop: asyncio.AbstractEventLoop = asyncio.get_event_loop()
        try:
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: UdpProtocol(self, loop),
                local_addr=(self.host, self.port),
                reuse_address=True,
            )
        except OSError as e:
            raise InboundTransportSetupError(
                "Unable to start UDP server with host "
                + f"'{self.host}' and port '{self.port}'\n"
            ) from e
        print(f"created inbound {self.host} {self.port}")
        self.transport = transport

    async def stop(self) -> None:
        """Stop this transport."""
        if self.transport:
            self.transport.close()
            self.transport = None

    async def inbound_message_handler(self, data: bytes, addr: str, proto: UdpProtocol):
        """
        Message handler for inbound messages.

        Args:
            conn: the active connection
            addr: the address of the sender
            loop: the asyncio event loop

        """

        print("inbound recv data:", addr, data)

        if not proto.socket_ref_id:
            if not proto.register:
                LOGGER.error("Cannot await socket reference for UDP connection")
            else:
                await proto.register

        print("inbound route data")

        try:
            # Route message and provide socket ref instance as means to respond
            await self.message_router(data, self._scheme, proto.socket_ref_id)
        except Exception:
            LOGGER.exception("Error handling message:")
