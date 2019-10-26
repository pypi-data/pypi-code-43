import requests

class Base():
    """
    Classe base para os métodos da API


    """

    def __init__(self,
                 auth= None,
                 session=None):

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

    def send(self, method = None, resource= None, headers=None, data = None, params= None):
        
        if(params is None):
            url = f'{self.uri}{resource}?xrfkey={self.xrfkey}'
        else:
            url = f"{self.uri}{resource}?xrfkey={self.xrfkey}&{params}"

        if(headers is None):
            headers = self.headers
        else:
            customHeaders = self.headers.copy()
            customHeaders.update(headers)
            headers = customHeaders.copy()

        request = requests.Request(method=method, url=url, data=data, headers=headers)
        prepared = request.prepare()
        response = self.session.send(
                                            prepared, 
                                            cert=(self.sslfile, self.sslfile_key), 
                                            verify=self.verify
                                            )

        try:
            self.response = dict(
                    status_code = response.status_code,
                    content = response.json()
            )
        except:
            self.response = dict(
                    status_code = response.status_code,
                    content = response.content.decode('utf-8')
            ) 
            
        finally:
            return self.response

        

    def get(self):
        self.method = 'GET'
        return self.send(method = self.method, resource= self.resource)

    def search(self, name):
        self.method = 'GET'
        params = f"filter=name eq '{name}'"
        return self.send(method = self.method, resource=self.resource, params=params)


    def search_by_id(self, id):
        self.method = 'GET'
        resource = f'{self.resource}/{id}'
        return self.send(method = self.method, resource= resource)

    def delete(self, id):
        method = 'DELETE'
        resource = f'{self.resource}/{id}'
        return self.send(method = method, resource= resource)