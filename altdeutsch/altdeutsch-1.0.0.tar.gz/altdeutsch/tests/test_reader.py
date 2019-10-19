"""

"""

import os
import unittest

from altdeutsch import PACKDIR
from altdeutsch.reader import read_export

__author__ = ["Clément Besnier <clemsciences@aol.com>", ]


class UnitTest(unittest.TestCase):

    def test_hildebrandslied(self):
        res = read_export(os.path.join(PACKDIR, "tests", "data", "hildebrandslied.txt"))

        self.assertEqual(list(res.keys()),
                         ['tok', 'lemma', 'inflection', 'verse', 'edition', 'pos', 'text', 'translation',
                          'lang', 'clause', 'inflectionClass', 'posLemma', 'rhyme', 'document',
                          'inflectionClassLemma'])

        self.assertEqual(res["tok"][0], ['Ik', 'gihorta', 'ðat', 'seggen', 'ðat', 'sih', 'urhettun', 'ænon', 'muotin'])
