from decorators import handle_response
from pyvxclient.resource import Resource


class ObjectMap(Resource):

    @handle_response
    def get(self, id=None, object_number=None, height=None, width=None):
        return self.client.object.getObjectMap(id=id, number=object_number, height=height, width=width).response()
