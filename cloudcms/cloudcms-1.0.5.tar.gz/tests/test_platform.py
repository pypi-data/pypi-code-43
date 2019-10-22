from .abstract_test import AbstractTest

class TestPlatform(AbstractTest):
    
    def test_platform(self):
        self.assertEqual("Root Platform", type(self).platform.data['title'])
        self.assertEqual("", type(self).platform.uri())
