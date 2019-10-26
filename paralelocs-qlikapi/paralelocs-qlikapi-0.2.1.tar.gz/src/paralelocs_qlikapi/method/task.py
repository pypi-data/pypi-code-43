from paralelocs_qlikapi.method.base import DefaultMethods

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
        method = 'POST'
        resource = 'task/start'
        params = f'name={name}'
        return self.send(method = method, resource= self.resource, params=params)


    def start_by_id(self, id):
        method = 'POST'
        resource = f'task/{id}/start'
        return self.send(method = method, resource= self.resource)
