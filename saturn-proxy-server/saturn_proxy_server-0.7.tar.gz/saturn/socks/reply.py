from ipaddress import IPv6Address, IPv4Address


class SocksReply:
    rep = 0

    def __init__(self, bind_addr=IPv4Address("0.0.0.0"), bind_port=0):
        self.ver = 5
        self.rsv = 0
        if isinstance(bind_addr, IPv4Address):
            self.atyp = 1
        elif isinstance(bind_addr, IPv6Address):
            self.atyp = 4
        else:
            self.atyp = 3
        self.bind_addr = bind_addr
        self.bind_port = bind_port

    def __bytes__(self):
        return self.ver.to_bytes(1, byteorder='big') + \
               self.rep.to_bytes(1, byteorder='big') + \
               self.rsv.to_bytes(1, byteorder='big') + \
               self.atyp.to_bytes(1, byteorder='big') + \
               int(self.bind_addr).to_bytes(4, byteorder='big') + \
               self.bind_port.to_bytes(2, byteorder='big')


class Success(SocksReply):
    pass


class Failure(SocksReply):
    rep = 1


class ConnectionNotAllowed(SocksReply):
    rep = 2


class NetworkUnreachable(SocksReply):
    rep = 3


class HostUnreachable(SocksReply):
    rep = 4


class ConnectionRefused(SocksReply):
    rep = 5


class TTLExpired(SocksReply):
    rep = 6


class CommandNotSupported(SocksReply):
    rep = 7


class AddressTypeNotSupported(SocksReply):
    rep = 8
