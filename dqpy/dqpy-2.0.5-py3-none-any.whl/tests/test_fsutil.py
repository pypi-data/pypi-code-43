import os
import unittest
from contextlib import suppress

from dq import fsutil


class TestFSUtil(unittest.TestCase):

    def tearDown(self):
        with suppress(Exception):
            fsutil.rmrf('test-files')

    def test_safe_mkdirp(self):
        fsutil.mkdirp('test-files/1/2/3')
        assert os.path.isdir('test-files/1/2/3')

    def test_safe_rmrf(self):
        fsutil.mkdirp('test-files/1/2')
        with open('test-files/1/2/3.txt', 'w') as f:
            f.write('hello')
        assert os.path.exists('test-files/1/2/3.txt')
        fsutil.rmrf('test-files/1/2/3.txt')
        assert not os.path.exists('test-files/1/2/3.txt')
        with open('test-files/1/2/3.txt', 'w') as f:
            f.write('hello')
        fsutil.rmrf('test-files')
        assert not os.path.exists('test-files')
        fsutil.rmrf('none')

    def test_traverse_error(self):
        self.assertRaises(FileNotFoundError, fsutil.traverse, 'none', None)
        self.assertRaises(
            NotADirectoryError, fsutil.traverse, 'README.md', None,
        )

    def test_traverse(self):
        fsutil.mkdirp('test-files/1/2')
        with open('test-files/1/2/3.txt', 'w') as f:
            f.write('hello')

        tree = {}

        def callback(path, isdir):
            assert path not in tree.keys()
            tree[path] = isdir

        fsutil.traverse('test-files', callback)
        assert tree == {'1': True, '1/2': True, '1/2/3.txt': False}

    def test_fileinfo(self):
        fsutil.mkdirp('test-files')
        with open('test-files/a.txt', 'w') as f:
            f.write('hello')
        assert fsutil.fileinfo('test-files/a.txt') == ('text/plain', 5, None)

    def test_safe_fileinfo(self):
        assert fsutil.safe_fileinfo(None) == (None, 0, None)
