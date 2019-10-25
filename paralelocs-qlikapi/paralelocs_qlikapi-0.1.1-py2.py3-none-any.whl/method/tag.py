from paralelocs_qlikapi.method.base import DefaultMethods, QlikRequest
import json


class Tag(DefaultMethods):
    """
    Classe para trabalhar com o recurso TAG da API do QLIK

    """

    def __init__(self,
                 auth= None,
                 session=None):
        super().__init__(auth=auth, session=session)
        self.resource = 'tag'

    def post(self, name):
        self.method = 'POST'
        body = dict(
                name = name,
                impactSecurityAccess = False,
                schemaPath = "Tag"
        )
        self.data = json.dumps(body)
        self.url = f'{self.uri}{self.resource}?xrfkey={self.xrfkey}'
        self.request = QlikRequest(self)
        return self.request.send()