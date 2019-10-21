from .cloudcms_object import CloudCMSObject

class RepositoryObject(CloudCMSObject):

    def __init__(self, repository, data):
        super(RepositoryObject, self).__init__(repository.client, data)

        self.repository = repository
        self.platform_id = repository.platform_id
        self.repository_id = repository._doc