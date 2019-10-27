from ipaddress import IPv4Address, IPv6Address


class SocksRequest:
    action_id: int

    def __init__(self, dispatcher, data):
        self.dispatcher = dispatcher
        self.ver = data[0]
        self.cmd = data[1]
        self.rsv = data[2]
        self.atyp = data[3]
        if self.atyp == 1:
            self.dst_addr = IPv4Address(data[4:-2])
        elif self.atyp == 3:
            self.dst_addr = data[5:5 + data[4]].decode()
        elif self.atyp == 4:
            self.dst_addr = IPv6Address(data[4:-2])
        self.dst_port = int.from_bytes(data[-2:], byteorder='big')

    async def go(self):
        pass

    @classmethod
    def parse(cls, dispatcher, data):
        assert data[0] == 5
        for sub in cls.__subclasses__():
            if sub.action_id == data[1]:
                return sub(dispatcher, data)
