from decorators import handle_response
from pyvxclient.resource import Resource


class Api(Resource):

    @handle_response
    def get(self):
        return self.client.api.getApi().response()
