from .cloudcms_object import CloudCMSObject
from .repository import Repository
from .request_error import RequestError

class Platform(CloudCMSObject):

    def __init__(self, client, data):
        super(Platform, self).__init__(client, data)

    def uri(self):
        return ''

    def list_repositories(self):
        uri = self.uri() + '/repositories'
        res = self.client.get(uri)
        return Repository.repository_map(self.client, res['rows'])

    def read_repository(self, repository_id):
        repository = None
        try:
            res = self.client.get('/repositories/' + repository_id)
            repository = Repository(self.client, res)
        except RequestError:
            repository = None
        
        return repository

    def create_repository(self, obj={}):
        uri = self.uri() + '/repositories'
        res = self.client.post(uri, obj)

        repository_id = res['_doc']        
        return self.read_repository(repository_id)