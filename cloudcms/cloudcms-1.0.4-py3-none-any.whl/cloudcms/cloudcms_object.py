from .request_error import RequestError

class CloudCMSObject(object):
    
    def __init__(self, client, data):
        self.client = client
        self._doc = data['_doc']

        self.data = data

    def uri(self):
        raise NotImplementedError()

    def reload(self):
        try:
            self.data = self.client.get(self.uri())
        except RequestError:
            self.data = None
            

    def delete(self):
        return self.client.delete(self.uri())

    def update(self):
        return self.client.put(self.uri(), data=self.data)