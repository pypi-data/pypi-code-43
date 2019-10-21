from .repository_object import RepositoryObject

class Node(RepositoryObject):

    def __init__(self, branch, data):
            super(Node, self).__init__(branch.repository, data)
            
            self.branch_id = branch._doc
            self.branch = branch

    def uri(self):
        return '%s/nodes/%s' % (self.branch.uri(), self._doc)

    @classmethod
    def node_map(cls, repository, data):
        return {node['_doc']: Node(repository, node) for node in data}