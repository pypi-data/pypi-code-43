import requests


class QlikRequest():
    """

        Classe de Prepara a Request
        Abstrai a criação de headers e SSL.
        retorna um dicionário com o status code e content

    """

    def __init__(self, 
                    request
                 ):
        self.method = request.method
        self.url = request.url
        self.data = request.data
        self.headers = request.headers
        self.session = request.session
        self.sslfile = request.sslfile
        self.sslfile_key = request.sslfile_key
        self.verify = request.verify
        self.request = requests.Request(method=self.method, url=self.url, data=self.data, headers=self.headers)
    

    def send(self):
        self.prepared = self.request.prepare()
        self.response = self.session.send(
                                            self.prepared, 
                                            cert=(self.sslfile, self.sslfile_key), 
                                            verify=self.verify
                                            )

        try:
            self.resp = dict(
                    status_code = self.response.status_code,
                    content = self.response.json()
            )
        except:
            self.resp = dict(
                    status_code = self.response.status_code,
                    content = self.response.content.decode('utf-8')
            ) 
            
        finally:
            return self.resp