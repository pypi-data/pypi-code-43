import unittest
import doctest
import io
import os
import time
import transcoding
from pathlib import Path


# def load_tests(loader, tests, ignore):
#     tests.addTests(doctest.DocTestSuite(transcoding))
#     return tests


class TranscodingTest(unittest.TestCase):
    """testing transcoding routines"""

    def test_inp(self):
        file_path = Path('.') / os.path.dirname(__file__) / "test_files/dummy.inp"
        file_path = str(file_path.resolve())
        with open(file_path, 'rb') as f:
            tc = transcoding.transcodings.inp.get_transcoding()
            content = (tc.read(f))
        self.assertListEqual(content['parts'][1]['node_index_3'], [4, 7, 1])


if __name__ == '__main__':
    unittest.main()
