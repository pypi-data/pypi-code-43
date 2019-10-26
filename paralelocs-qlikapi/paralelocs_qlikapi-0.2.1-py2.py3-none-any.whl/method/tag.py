from paralelocs_qlikapi.method.base import DefaultMethods
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
        method = 'POST'
        body = dict(
                name = name,
                impactSecurityAccess = False,
                schemaPath = "Tag"
        )
        data = json.dumps(body)

        return self.send(method = method, resource= self.resource, data=data)