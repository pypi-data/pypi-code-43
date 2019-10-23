import requests
import json
from paralelocs_qlikapi.method.base import DefaultMethods, QlikRequest

class App(DefaultMethods):
    """
    Classe para trabalhar com o recurso APP da API do QLIK

    """

    def __init__(self,
                 auth= None,
                 session=None):
        super().__init__(auth=auth, session=session)
        self.resource = 'app'

    def post(self, path, name, filename):

        self.resource = 'app/upload'
        self.method = 'POST'
        self.headers['Content-Type']= 'application/vnd.qlik.sense.app'
        self.queryparams = f'name={name}&keepdata=false'
        self.data = open(f'{path}/{filename}','rb').read()
        self.url = f'{self.uri}{self.resource}?xrfkey={self.xrfkey}&{self.queryparams}'
        self.request = QlikRequest(self)
        return self.request.send()


    def reload(self, name):
        app = self.search(name=name)
        app = app['content'][0]
        appid = app['id']
        self.resource = f'app/{appid}/reload'
        self.method = 'POST'
        self.data = ''
        self.url = f'{self.uri}{self.resource}?xrfkey={self.xrfkey}'
        self.request = QlikRequest(self)
        return self.request.send()