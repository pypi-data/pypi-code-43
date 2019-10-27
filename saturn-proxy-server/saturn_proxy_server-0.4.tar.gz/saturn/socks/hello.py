from saturn import state


class SocksHello:
    def __init__(self, dispatcher, data):
        self.ver = 5
        self.dispatcher = dispatcher
        self.nmethods = data[1]
        self.methods = [x for x in data[2:2 + self.nmethods]]

    def reply(self):
        for m in self.dispatcher.server.server_auth_methods:
            if m in self.methods:
                self.dispatcher.state = state.WaitingAuthenticationData(method=m) if not m == 0 \
                    else state.Authenticated()
                return self.ver.to_bytes(1, byteorder='big') + int.to_bytes(m, 1, byteorder='big')
        return self.ver.to_bytes(1, byteorder='big') + int.to_bytes(255, 1, byteorder='big')
