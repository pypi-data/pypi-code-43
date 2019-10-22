import json
from .repository_object import RepositoryObject
from .request_error import RequestError
from .node import Node

class Branch(RepositoryObject):

    def __init__(self, repository, data):
        super(Branch, self).__init__(repository, data)

    def uri(self):
        return '%s/branches/%s' % (self.repository.uri(), self._doc) 

    def is_master(self):
        return self.data['type'] == 'MASTER'

    def read_node(self, node_id):
        uri = self.uri() + "/nodes/" + node_id
        node = None
        try:
            res = self.client.get(uri)
            node = Node(self, res)
        except RequestError:
            node = None

        return node
    
    def query_nodes(self, query, pagination={}):
        uri = self.uri() + "/nodes/query"

        res = self.client.post(uri, params=pagination, data=query)
        return Node.node_map(self, res['rows'])

    def find_nodes(self, config, pagination={}):
        uri = self.uri() + "/nodes/find"

        res = self.client.post(uri, params=pagination, data=config)
        return Node.node_map(self, res['rows'])

    def create_node(self, obj, options={}):
        uri = self.uri() + "/nodes"

        params = {}
        params['rootNodeId'] = options.get('rootNodeId') or 'root'
        params['associationType'] = options.get('associationType') or 'a:child'

        if 'parentFolderPath' in options:
            params['parentFolderPath'] = options['parentFolderPath']
        elif 'folderPath' in options:
            params['parentFolderPath'] = options['folderPath']
        elif 'folderpath' in options:
            params['parentFolderPath'] = options['folderpath']  
        
        if 'filePath' in options:
            params['filePath'] = options['filePath']
        elif 'filepath' in options:
            params['filePath'] = options['filepath']

        res = self.client.post(uri, params=params, data=obj)
        node_id = res['_doc']

        return self.read_node(node_id)

    def delete_nodes(self, node_ids):
        uri = self.uri() + '/nodes/delete'
        return self.client.post(uri, data=node_ids)

    @classmethod
    def branch_map(cls, repository, data):
        return {branch['_doc']: Branch(repository, branch) for branch in data}