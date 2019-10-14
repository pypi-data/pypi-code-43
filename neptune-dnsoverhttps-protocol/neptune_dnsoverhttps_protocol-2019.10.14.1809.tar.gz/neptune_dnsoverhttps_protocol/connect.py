from .protocol import Protocol


class Connection:

    def __init__(self, dispatcher_cls, loop, cert_path, key_path, prefix='dns-request', host='0.0.0.0', port=443, with_ssl=True):
        self.dispatcher_cls = dispatcher_cls
        self.loop = loop
        self.cert_path = cert_path
        self.key_path = key_path
        self.prefix = prefix
        self.host = host
        self.port = port
        self.with_ssl = with_ssl

    async def start(self):
        print('Starting DNS-over-HTTPS server')
        await Protocol(self).start()