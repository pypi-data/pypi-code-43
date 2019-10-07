from django.test import TestCase
from .models import FSFile


class TestCases(TestCase):

    def test_001(self):

        object_test_package = FSFile.objects.create()

        object_test_package.size = 4453453
        object_test_package.mime_type = 'application/x-tar'
        object_test_package.path = '/test/file.tar.gz'
        object_test_package.save()

        self.assertEqual(object_test_package.size, 4453453)
        self.assertEqual(
            object_test_package.mime_type, 'application/x-tar')
        self.assertEqual(object_test_package.path, '/test/file.tar.gz')
