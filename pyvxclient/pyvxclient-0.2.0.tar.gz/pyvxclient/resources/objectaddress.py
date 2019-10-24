from decorators import handle_response
from pyvxclient.resource import Resource


class ObjectAddress(Resource):

    @handle_response
    def get(self, object_number):
        return self.client.object.getObjectAddress(object_number=object_number).response()
