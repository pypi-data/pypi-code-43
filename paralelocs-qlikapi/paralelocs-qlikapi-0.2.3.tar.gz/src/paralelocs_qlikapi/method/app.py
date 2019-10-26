import requests
import json
from paralelocs_qlikapi.method.base import DefaultMethods
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

        resource = 'app/upload'
        method = 'POST'
        headers = {}
        headers['Content-Type']= 'application/vnd.qlik.sense.app'
        queryparams = f'name={name}&keepdata=false'

        try:
            data = open(f'{path}/{filename}','rb').read()
        except FileNotFoundError as e:
            print(f'{e}\n QVF file not found.')
            data = ''
        
        return self.send(method = method, resource=resource, params=queryparams, headers=headers, data=data)


    def reload(self, name):
        app = self.search(name=name)
        app = app['content'][0]
        appid = app['id']
        resource = f'app/{appid}/reload'
        method = 'POST'
        data = ''
        self.url = f'{self.uri}{self.resource}?xrfkey={self.xrfkey}'
        self.request = QlikRequest(self)
        return self.send(method = method, resource=resource, data=data)

    # INCLUIR TAG BY APP ID
    def add_tag(self, appid, tagname):

        ##### RECUPERA DADOS DA APP ###########

        # appname = self.search(name=appname)
        # exist_app = appname['content'][0]
        # appid = exist_app['id']
        
        app = self.search_by_id(id=appid)['content']

        ##### VERIFICA SE TAGS EXISTE ###########
        tagapi = Tag(auth = self.auth, session= self.session)
        existing_tags = tagapi.search(name = tagname)['content']

        if (len(existing_tags) > 0):
            _tag = existing_tags[0]
        else:
            _tag = tagapi.post(name=tagname)['content']
            

        ##### DEFINI RECURSO E METODO ###########    
        resource = f'app/{appid}'
        method = 'PUT'
        

        ###### CRIA BODY COM TAG ################
        tags = []
        tags.append(_tag)
        tags_dict = dict(tags = tags)
        app.update(tags_dict)
        data = json.dumps(app)

        return self.send(method = method, resource=resource, data=data)

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
            raise AttributeError ('Stream not found')
                   

        ##### DEFINI RECURSO E METODO ###########    
        resource = f'app/{appid}/publish'
        method = 'PUT'

        ###### CRIA QUERY PARAMTERS ################
        params = f'stream={_stream}'

        return self.send(method = method, resource=resource, params=params)


    def unpublish(self, id):

        """
            DESPUBLICAR APP

        """
        resource = f'app/{id}/unpublish'
        method = 'POST'
        data = ''
        return self.send(method = method, resource=resource, data=data)
