from .abstract_test import AbstractTest
from cloudcms.repository import Repository

class AbstractWithRepositoryTest(AbstractTest):
    
    @classmethod
    def setUpClass(cls):
        super(AbstractWithRepositoryTest, cls).setUpClass()
        cls.repository = cls.platform.create_repository()

    @classmethod
    def tearDownClass(cls):
        cls.repository.delete()

