from apistar.client.transports import HTTPTransport
from apistar.client.encoders import JSONEncoder, MultiPartEncoder, URLEncodedEncoder
from arkindex.encoders import XMLEncoder


class ArkindexHTTPTransport(HTTPTransport):
    default_encoders = [
        JSONEncoder(),
        MultiPartEncoder(),
        URLEncodedEncoder(),
        XMLEncoder(),
    ]

    def get_request_options(self, *args, **kwargs):
        options = super().get_request_options(*args, **kwargs)
        options['timeout'] = (30, 60)
        return options
