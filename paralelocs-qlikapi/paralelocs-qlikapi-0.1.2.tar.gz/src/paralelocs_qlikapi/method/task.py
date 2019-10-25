from paralelocs_qlikapi.method.base import DefaultMethods, QlikRequest

class Task(DefaultMethods):
    """
    Classe para trabalhar com o recurso APP da API do QLIK

    """

    def __init__(self,
                 auth= None,
                 session=None):
        super().__init__(auth=auth, session=session)
        self.resource = 'task'


    def start_by_name(self, name):
        self.method = 'POST'
        self.resource = 'task/start'
        self.url = f"{self.uri}{self.resource}?xrfkey={self.xrfkey}&name={name}"
        self.request = QlikRequest(self)
        return self.request.send()


    def start_by_id(self, id):
        self.method = 'POST'
        self.resource = f'task/{id}/start'
        self.url = f"{self.uri}{self.resource}?xrfkey={self.xrfkey}"
        self.request = QlikRequest(self)
        return self.request.send()
