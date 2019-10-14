from aiohttp import web
import ssl
import base64
import json


class Protocol:
    def __init__(self, connector):
        self.connector = connector
        self.app = web.Application(loop=self.connector.loop)
        self.app.add_routes([web.get(f'/{connector.prefix}', self.handle)])
        if connector.with_ssl:
            self.ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
            self.ssl_context.load_cert_chain(connector.cert_path, connector.key_path)

    async def handle(self, request):
        dispatcher = self.connector.dispatcher_cls(loop=self.connector.loop)
        try:
            if request.method == 'GET':
                query = request.rel_url.query['dns']
                decoded_query = base64.b64decode(query + '=' * (4 - len(query) % 4))
                result = await dispatcher.handle(decoded_query)
                return web.Response(text=base64.b64encode(result).decode('ascii'), content_type='application/dns-message')
            elif request.method == 'POST':
                data = await request.json(loads=json.loads)
                query = data['dns']
                decoded_query = base64.b64decode(query + '=' * (4 - len(query) % 4))
                result = await dispatcher.handle(decoded_query)
                return web.Response(text=base64.b64encode(result).decode('ascii'), content_type='application/dns-message')
        except KeyError:
            return web.Response(text='Error', content_type='application/dns-message')
        return web.Response(text='', content_type='application/dns-message')

    async def start(self):
        await web._run_app(self.app, port=self.connector.port, host=self.connector.host)
