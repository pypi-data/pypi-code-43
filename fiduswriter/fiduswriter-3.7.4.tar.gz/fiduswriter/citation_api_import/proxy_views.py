from tornado.web import RequestHandler, HTTPError
from tornado.httpclient import AsyncHTTPClient
from base.django_handler_mixin import DjangoHandlerMixin

ALLOWED_DOMAINS = {
    'search.gesis.org': True,
    'api.datacite.org': True
}


class Proxy(DjangoHandlerMixin, RequestHandler):
    async def get(self, url):
        user = self.get_current_user()
        domain = url.split('/')[2]
        if domain not in ALLOWED_DOMAINS or not user.is_authenticated:
            self.set_status(401)
            self.finish()
            return
        query = self.request.query
        if query:
            url += '?' + query
        http = AsyncHTTPClient()
        response = await http.fetch(
            url,
            method='GET'
        )
        if not response.error:
            self.write(response.body)
        self.finish()
