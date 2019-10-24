from .abstract_with_repository_test import AbstractWithRepositoryTest
from cloudcms.branch import Branch

class TestBranch(AbstractWithRepositoryTest):
    
    def test_branches(self):
        repository = type(self).repository

        branches = repository.list_branches()
        self.assertTrue(len(branches) > 0)
        for branch in branches.values():
            self.assertIsInstance(branch, Branch)

        master = repository.read_branch('master')
        self.assertEqual('/repositories/' + repository._doc + '/branches/' + branch._doc, branch.uri())
        self.assertTrue(master.is_master())

        branch = repository.read_branch('I am not real')
        self.assertIsNone(branch)




