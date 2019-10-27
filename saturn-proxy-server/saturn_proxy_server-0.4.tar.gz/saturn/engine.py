import asyncio
import typing
from ipaddress import IPv4Address, IPv6Address
from saturn import protocol, config


class Server:
    def __init__(self, host: typing.Union[IPv6Address, IPv4Address, str],
                 port: int,
                 tcp:bool=True, udp=False, custom_auth=None):
        self.host = host
        self.port = port
        self.tcp = tcp
        self.udp = udp
        self.auth_methods = []
        self.auth_config = config.AUTHENTICATION_METHODS if custom_auth is None else custom_auth

    def init_auth_methods(self):
        for method in self.auth_config:
            m = __import__(method, globals=globals(), fromlist=[""])
            self.auth_methods.append(m.Authenticator(**getattr(config, method.upper().replace(".", "_"), {})))
        if not self.auth_methods:
            raise Exception("Server have no auth methods. Please fill in AUTHENTICATION_METHODS")

    @property
    def server_auth_methods(self):
        return [x.method for x in self.auth_methods]

    async def auth(self, method, *args, **kwargs):
        for m in self.auth_methods:
            if m.method == method:
                return await m.authenticate(*args, **kwargs)
        else:
            return False

    def start(self):
        loop = asyncio.new_event_loop()
        self.init_auth_methods()
        if self.tcp:
            loop.create_task(protocol.Socks5TcpServer(self, loop).start_server(self.host, self.port))
        loop.run_forever()
