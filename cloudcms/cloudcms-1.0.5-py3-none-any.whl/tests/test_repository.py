from .abstract_test import AbstractTest
from cloudcms.repository import Repository

class TestRepository(AbstractTest):
    
    def test_repositories(self):
        platform = type(self).platform

        repositories = platform.list_repositories()
        self.assertTrue(len(repositories) > 0)
        for rep in repositories.values():
            self.assertIsInstance(rep, Repository)

        repository = platform.create_repository()
        self.assertIsInstance(repository, Repository)
        self.assertEqual('/repositories/' + repository._doc, repository.uri())

        repositoryRead = platform.read_repository(repository._doc)
        self.assertEqual(repository.data, repositoryRead.data)

        repository.delete()
        repositoryRead = platform.read_repository(repository._doc)
        self.assertIsNone(repositoryRead)

        repository = platform.read_repository('I am not real')
        self.assertIsNone(repository)     
