import requests
import json
from paralelocs_qlikapi.method.base import DefaultMethods, QlikRequest
from paralelocs_qlikapi.method.tag import Tag
from paralelocs_qlikapi.method.stream import Stream

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

        ### INCLUIR TRY ########
        # self.data = open(f'{path}/{filename}','rb').read()
        # FileNotFoundError: [Errno 2] No such file or directory: '/Goot/6.Misc/Appllication/temp.qvf'
        try:
            self.data = open(f'{path}/{filename}','rb').read()
        except FileNotFoundError as e:
            print(f'{e}\n QVF file not found.')
            self.data = ''

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

    # INCLUIR TAG BY APP ID
    def add_tag(self, appid, tagname):

        ##### RECUPERA DADOS DA APP ###########

        # appname = self.search(name=appname)
        # exist_app = appname['content'][0]
        # appid = exist_app['id']
        # app = self.search_by_id(id=appid)['content']

        ##### VERIFICA SE TAGS EXISTE ###########
        tagapi = Tag(auth = self.auth, session= self.session)
        existing_tags = tagapi.search(name = tagname)['content']

        if (len(existing_tags) > 0):
            _tag = existing_tags[0]
        else:
            _tag = tagapi.post(name=tagname)['content']
            

        ##### DEFINI RECURSO E METODO ###########    
        self.resource = f'app/{appid}'
        self.method = 'PUT'

        ###### CRIA BODY COM TAG ################
        tags = []
        tags.append(_tag)
        tags_dict = dict(tags = tags)
        app.update(tags_dict)
        self.data = json.dumps(app)
        self.url = f'{self.uri}{self.resource}?xrfkey={self.xrfkey}'
        self.request = QlikRequest(self)

        return self.request.send()

    # INCLUIR PUBLISH BY APP ID
    def publish_to_stream(self, appid, streamname):
        """

            PUBLICAR APP NA STREAM


        """

        ##### RECUPERA DADOS DA APP ###########

        # appname = self.search(name=appname)
        # exist_app = appname['content'][0]
        # appid = exist_app['id']

        ##### VERIFICA SE EXISTE STREAM ###########
        streamapi = Stream(auth = self.auth, session= self.session)
        existing_stream = streamapi.search(name = streamname)['content']

        if (len(existing_stream) > 0):
            _stream= existing_stream[0]['id']
        else:
            _stream = streamapi.post(name=streamname)['content']
            

        ##### DEFINI RECURSO E METODO ###########    
        self.resource = f'app/{appid}/publish'
        self.method = 'PUT'

        ###### CRIA QUERY PARAMTERS ################
        
        self.url = f"{self.uri}{self.resource}?xrfkey={self.xrfkey}&stream={_stream}"
        self.request = QlikRequest(self)

        return self.request.send()


    def unpublish(self, name):

        """
            DESPUBLICAR APP

        """
        
        app = self.search(name=name)
        app = app['content'][0]
        appid = app['id']
        self.resource = f'app/{appid}/unpublish'
        self.method = 'POST'
        self.data = ''
        self.url = f'{self.uri}{self.resource}?xrfkey={self.xrfkey}'
        self.request = QlikRequest(self)
        return self.request.send()
