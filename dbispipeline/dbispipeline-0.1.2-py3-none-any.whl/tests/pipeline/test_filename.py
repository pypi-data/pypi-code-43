# -*- coding: utf-8 -*-
import unittest
import tempfile

from dbispipeline.pipeline.filename import FileReader
from dbispipeline.pipeline.filename import FileWriter
from dbispipeline.pipeline.filename import PathTransformer


class TestFileNames(unittest.TestCase):

    def test_text(self):
        tmpfiles = [
            tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
            for x in range(10)
        ]
        tmpnames = [f.name for f in tmpfiles]
        contents = [f'file {i}' for i in range(10)]
        transformer = FileWriter(filenames=tmpnames, writemode='text')
        transformer.transform(contents)
        reader = FileReader(mode='text')
        read_contents = reader.transform(tmpnames)
        self.assertEqual(contents, read_contents)

    def test_json(self):
        tmpfiles = [
            tempfile.NamedTemporaryFile(
                mode='w', suffix='.json', delete=False) for x in range(10)
        ]
        tmpnames = [f.name for f in tmpfiles]
        contents = [{'int': i, 'list': [], 'string': 'foo'} for i in range(10)]
        transformer = FileWriter(filenames=tmpnames, writemode='json')
        transformer.transform(contents)
        reader = FileReader(mode='json')
        read_contents = reader.transform(tmpnames)
        self.assertEqual(contents, read_contents)

    def test_pickle(self):
        tmpfiles = [
            tempfile.NamedTemporaryFile(
                mode='wb', suffix='.pickle', delete=False) for x in range(10)
        ]
        tmpnames = [f.name for f in tmpfiles]
        contents = [{'int': i, 'list': [], 'string': 'foo'} for i in range(10)]
        transformer = FileWriter(filenames=tmpnames, writemode='pickle')
        transformer.transform(contents)
        reader = FileReader(mode='pickle')
        read_contents = reader.transform(tmpnames)
        self.assertEqual(contents, read_contents)

    def test_path_renamer_noextension(self):
        transformer = PathTransformer('grammar')
        documents = ['/some/file/a.txt', '/some/file/b', '/some/file/c.blob']
        expected = [
            '/some/file/grammar/a.txt',
            '/some/file/grammar/b',
            '/some/file/grammar/c.blob',
        ]
        actual = transformer.transform(documents)
        self.assertEqual(actual, expected)

    def test_path_renamer_extension(self):
        transformer = PathTransformer('grammar', extension='.json')
        documents = ['/some/file/a.txt', '/some/file/b', '/some/file/c.blob']
        expected = [
            '/some/file/grammar/a.json',
            '/some/file/grammar/b.json',
            '/some/file/grammar/c.json',
        ]
        actual = transformer.transform(documents)
        self.assertEqual(actual, expected)
