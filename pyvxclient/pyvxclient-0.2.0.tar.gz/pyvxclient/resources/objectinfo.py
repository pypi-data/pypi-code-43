from decorators import handle_response
from pyvxclient.resource import Resource


class ObjectInfo(Resource):

    @handle_response
    def get(self, object_number):
        return self.client.object.getObjectInfo(number=object_number).response()
