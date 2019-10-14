from django.core.files.base import ContentFile
import os
import shutil
import unittest
from _pytest.monkeypatch import MonkeyPatch
from publishing_boy import config
from publishing_boy.tests.utils import get_test_storage
from publishing_boy.process import (
    build_tuple,
    file_tuples,
    save_content,
    create_content_folder,
)


class ProcessTest(unittest.TestCase):
    def setUp(self):
        """Prepare file tests"""
        self.monkeypatch = MonkeyPatch()
        self.filename = 'testing/test_post.md'
        self.content = 'This is my content.'
        temp_dir, storage = get_test_storage()
        self.temp_dir = temp_dir
        self.storage = storage
        self.storage.save(self.filename, ContentFile(self.content))

        self.content_temp_dir, self.content_storage = get_test_storage()

    def result_tuple(self):
        return (
            os.path.basename(self.filename),
            self.filename,
            os.path.abspath(self.storage.path(self.filename)),
            self.content,
        )

    def tearDown(self):
        """Remove temp dir"""
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.content_temp_dir)

    def test_setup(self):
        self.assertFalse(self.storage.exists('testing/second.md'))
        self.assertTrue(self.storage.exists(self.filename))

    def test_build_tuple(self):
        _, path, abspath, _ = self.result_tuple()
        result = build_tuple(path, abspath)

        assert result == self.result_tuple()

    def test_file_tuples(self):
        assert list(file_tuples(
            self.storage.path(''))) == [self.result_tuple()]

    def test_save_content(self):

        config['Instance'] = {'content_dir': self.content_temp_dir}

        saved_filename = save_content(self.result_tuple())

        assert saved_filename
        assert self.content_storage.exists(saved_filename)

    def test_create_content_folder(self):
        folders = [
            os.path.join(self.temp_dir, test_dir)
            for test_dir in ['a', 'b/c', 'd/e/f']
        ]

        for folder in folders:
            with self.subTest():
                create_content_folder(folder)
                assert self.storage.exists(folder)

        # try doing the same thing one more time
        for folder in folders:
            with self.subTest():
                create_content_folder(folder)
                assert self.storage.exists(folder)
