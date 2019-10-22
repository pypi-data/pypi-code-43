from .cloudcms_object import CloudCMSObject
from .branch import Branch
from .request_error import RequestError


class Repository(CloudCMSObject):

    def __init__(self, client, data):
        super(Repository, self).__init__(client, data)

        self.platform_id = data['platformId']

    def uri(self):
        return '/repositories/' + self._doc

    def list_branches(self):
        uri = self.uri() + '/branches/'
        res = self.client.get(uri)
        return Branch.branch_map(self, res['rows'])

    def read_branch(self, branch_id):
        uri = self.uri() + '/branches/' + branch_id
        branch = None
        try:
            res = self.client.get(uri)
            branch = Branch(self, res)
        except RequestError:
            branch = None

        return branch
            

    def create_branch(self, obj={}):
        uri = self.uri() + '/branches'
        res = self.client.post(uri, obj)

        branch_id = res["_doc"]
        return self.read_branch(branch_id)
        
    @classmethod
    def repository_map(cls, client, data):
        return {repository['_doc']: Repository(client, repository) for repository in data}