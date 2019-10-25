from paralelocs_qlikapi.method.request import QlikRequest


class Base():
    """
    Classe base para os métodos da API


    """

    def __init__(self,
                 auth= None,
                 session=None):

        self.resource = None
        self.method = None
        self.data = None
        self.headers = auth.headers
        self.uri = auth.uri
        self.sslfile = auth.sslfile
        self.sslfile_key = auth.sslfile_key
        self.xrfkey = auth.xrfkey
        self.verify = auth.verify
        self.session = session
        self.auth = auth

    def get(self):
        raise NotImplementedError

    def search(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError

class DefaultMethods(Base):

    def get(self):
        self.method = 'GET'
        self.url = f"{self.uri}{self.resource}?xrfkey={self.xrfkey}"
        self.request = QlikRequest(self)
        return self.request.send()

    def search(self, name):
        self.method = 'GET'
        self.url = f"{self.uri}{self.resource}?xrfkey={self.xrfkey}&filter=name eq '{name}'"
        self.request = QlikRequest(self)
        return self.request.send()


    def search_by_id(self, id):
        self.method = 'GET'
        self.url = f"{self.uri}{self.resource}/{id}?xrfkey={self.xrfkey}"
        self.request = QlikRequest(self)
        return self.request.send()

    def delete(self, id):
        self.method = 'GET'
        self.url = f"{self.uri}{self.resource}/{id}?xrfkey={self.xrfkey}"
        self.request = QlikRequest(self)
        return self.request.send()