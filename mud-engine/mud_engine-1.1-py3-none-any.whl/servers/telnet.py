import asyncio
import logging
from ..base import MUDObject
from ..communication import MUDMessage
from ..player import ConnectingPlayer
from ..servers.base import MUDClientConnection
from ..servers.base import MUDServer
from colors import blue as ansi_blue
from colors import black as ansi_black
from colors import cyan as ansi_cyan
from colors import green as ansi_green
from colors import white as ansi_white
from colors import magenta as ansi_magenta
from colors import none as ansi_nocolor
from colors import red as ansi_red
from colors import white as ansi_white
from colors import yellow as ansi_yellow

nocolor = '\x1b[0m'

class TelnetMessage(MUDMessage):

    color_map = {
        "nocolor": '\x1b[0m',
        "blue": ansi_blue("", style="faint").replace(nocolor, ""),
        "brown": ansi_yellow("", style="faint+bold").replace(nocolor, ""),
        "cyan": ansi_cyan("", style="faint").replace(nocolor, ""),
        "green": ansi_green("", style="faint").replace(nocolor, ""),
        "grey": ansi_white("", style="faint").replace(nocolor, ""),
        "lightblue": ansi_blue("").replace(nocolor, ""),
        "lightcyan": ansi_cyan("").replace(nocolor, ""),
        "lightgreen": ansi_green("").replace(nocolor, ""),
        "lightred": ansi_red("").replace(nocolor, ""),
        "magenta": ansi_magenta("", style="faint").replace(nocolor, ""),
        "pink": ansi_magenta("").replace(nocolor, ""),
        "red": ansi_red("").replace(nocolor, ""),
        "white": ansi_white("").replace(nocolor, ""),
        "yellow": ansi_yellow("").replace(nocolor, ""),
    }

    def __str__(self):

        message = self.message

        for color_name, color in MUDMessage._colors.items():
            color_code = color.color_code
            replace_color = self.color_map.get(color_name, "")
            message = message.replace(color_code, replace_color)

        return message
class TelnetClientConnection(asyncio.Protocol, MUDClientConnection):

    server = None
    transport = None
    connection_id = None

    # def __str__(self):
    #     return "{}({}, <{}>)".format(self.__class__.__name__, self.socket, self.address)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.buffer = ""

    def __del__(self):
        logging.debug("Deleting {}".format(self))

    def connection_made(self, transport: asyncio.transports.BaseTransport) -> None:
        self.transport = transport
        self.connection_id = ":".join([str(v) for v in self.transport.get_extra_info("peername", tuple())])
        self.server.add_client(self)
        self.player = ConnectingPlayer(client=self)
        self.player.send_message("What name would you like on your tombstone? ")
        self.player.handle_login()

    def connection_lost(self, exc):
        self.server.remove_client(self)
        self.player = None
        logging.debug(f"Tearing down TelnetClientConnection {self}")

    def disconnect(self):
        self.server.remove_client(self)
        self.player = None
        self.transport.close()
        logging.debug(f"Disconnecting client {self}")

    def parse_message(self, message):
        return TelnetClientConnection.IncomingTelnetMessage(self, message)

    def data_received(self, data: bytes) -> None:
        """
        Comes from asyncio.Protocol - will be called when the client sends data
        """

        message = self.parse_message(data.decode("latin1"))

        if message is None:
            return

        self.buff = message.data
        self.player.handle_command(message.message.strip())

    def send_message(self, message):
        msg = str(TelnetMessage(message))
        self.buff = msg
        self.transport.write((msg).encode())

    class IncomingTelnetMessage(MUDObject):

        # Different states we can be in while reading data from client
        # See _process_sent_data function
        _READ_STATE_NORMAL = 1
        _READ_STATE_COMMAND = 2
        _READ_STATE_SUBNEG = 3

        # Command codes used by Telnet protocol
        # See _process_sent_data function
        _TN_INTERPRET_AS_COMMAND = 255
        _TN_ARE_YOU_THERE = 246
        _TN_WILL = 251
        _TN_WONT = 252
        _TN_DO = 253
        _TN_DONT = 254
        _TN_SUBNEGOTIATION_START = 250
        _TN_SUBNEGOTIATION_END = 240

        def __bool__(self):
            return True if self.message else False

        def __init__(self, client, data):
            super().__init__()
            self.client = client
            self.data = data
            self.message = self._clean_message()

        def _clean_message(self):

            # start with no message and in the normal state
            message = ''
            state = self._READ_STATE_NORMAL

            # go through the data a character at a time
            for c in self.data:

                # handle the character differently depending on the state we're in:

                # normal state
                if state == self._READ_STATE_NORMAL:

                    # if we received the special 'interpret as command' code,
                    # switch to 'command' state so that we handle the next
                    # character as a command code and not as regular text data
                    if ord(c) == self._TN_INTERPRET_AS_COMMAND:
                        state = self._READ_STATE_COMMAND

                    # if we get a newline character, this is the end of the
                    # message. Set 'message' to the contents of the buffer and
                    # clear the buffer
                    elif c == "\n":
                        message = self.client.buffer
                        self.client.buffer = ""

                    # some telnet clients send the characters as soon as the user
                    # types them. So if we get a backspace character, this is where
                    # the user has deleted a character and we should delete the
                    # last character from the buffer.
                    elif c == "\x08":
                        self.client.buffer = self.client.buffer[:-1]

                    # otherwise it's just a regular character - add it to the
                    # buffer where we're building up the received message
                    else:
                        self.client.buffer += c

                # command state
                elif state == self._READ_STATE_COMMAND:

                    # the special 'start of subnegotiation' command code indicates
                    # that the following characters are a list of options until
                    # we're told otherwise. We switch into 'subnegotiation' state
                    # to handle this
                    if ord(c) == self._TN_SUBNEGOTIATION_START:
                        state = self._READ_STATE_SUBNEG

                    # if the command code is one of the 'will', 'wont', 'do' or
                    # 'dont' commands, the following character will be an option
                    # code so we must remain in the 'command' state
                    elif ord(c) in (self._TN_WILL, self._TN_WONT, self._TN_DO,
                                    self._TN_DONT):
                        state = self._READ_STATE_COMMAND

                    # for all other command codes, there is no accompanying data so
                    # we can return to 'normal' state.
                    else:
                        state = self._READ_STATE_NORMAL

                # subnegotiation state
                elif state == self._READ_STATE_SUBNEG:

                    # if we reach an 'end of subnegotiation' command, this ends the
                    # list of options and we can return to 'normal' state.
                    # Otherwise we must remain in this state
                    if ord(c) == self._TN_SUBNEGOTIATION_END:
                        state = self._READ_STATE_NORMAL

            # return the contents of 'message' which is either a string or None
            return message

class TelnetServer(MUDServer):

    port = "localhost"
    host = 5000
    clients = {}
    _server = None

    def remove_client(self, client: MUDClientConnection) -> None:
        if client.connection_id in self.clients:
            del self.clients[client.connection_id]

    def add_client(self, client: MUDClientConnection) -> None:
        self.clients[client.connection_id] = client

    def __init__(self, host:str=None, port:int=None):
        super().__init__()

        self.port = port or self.port
        self.host = host or self.host
        self.clients = {}

    def shutdown(self):
        self._server.close()

    async def run(self):

        logging.info(f"TelnetServer starting on {self.host}:{self.port}")

        class _SocketConnection(TelnetClientConnection):
            def __init__(s, *args, **kwargs):
                super().__init__(*args, **kwargs)
                s.server = self

        loop = asyncio.get_running_loop()
        self._server = await loop.create_server(_SocketConnection, self.host, self.port)
        try:
            await self._server.serve_forever()
        except asyncio.CancelledError:
            pass
