from .core import Session
from .responses import PagedResponse
from . import exceptions


class Client(Session):
    def request(self, method, url, *args, **kwargs):
        self.limit = kwargs.pop('limit', -1)
        return super(Session, self).request(method, url, *args, **kwargs)

    def send(self, request, **kwargs):
        response = super(Client, self).send(request, **kwargs)

        if response.headers.get('content-length') == '0':
            return {}
        try:
            data = response.json()
        except ValueError:
            raise exceptions.BadJSON(response)

        limit = self.limit
        self.limit = -1  # reset the limit again
        if 'pageItemList' in data:
            return PagedResponse(super(Session, self), response, limit=limit)
        elif 'itemList' in data:
            return data['itemList']
        elif 'testRunList' in data:
            return data['testRunList']
        elif 'dtoSample' in data:
            return data['dtoSample']
        else:
            return data
