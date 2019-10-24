from decorators import handle_response
from pyvxclient.resource import Resource


class Place(Resource):

    @handle_response
    def get(self):
        return self.client.customer.getPlace().response()
