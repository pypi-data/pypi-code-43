from collections import OrderedDict
from .repository_object import RepositoryObject

class Node(RepositoryObject):

    def __init__(self, branch, data):
            super(Node, self).__init__(branch.repository, data)
            
            self.branch_id = branch._doc
            self.branch = branch

    def uri(self):
        return '%s/nodes/%s' % (self.branch.uri(), self._doc)

    def download_attachment(self, attachment_id='default'):
        uri = self.uri() + '/attachments/' + attachment_id

        return self.client.get(uri, output_json=False)

    def upload_attachment(self, attachment_id, file, content_type):
        uri = self.uri() + '/attachments/' + attachment_id

        return self.client.upload(uri, attachment_id, file, content_type)

    @classmethod
    def node_map(cls, repository, data):
        return OrderedDict((node['_doc'], Node(repository, node)) for node in data)
