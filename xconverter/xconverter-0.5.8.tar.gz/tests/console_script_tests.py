import unittest

from converter import console_script


class Conversor(unittest.TestCase):

    def test_attach_suffix(self):

        result = console_script.attach_suffix(
            'eruditarticle/erudit:erudit.approchesind0522.approchesind01992.1032264ar.xml',
            'suffix',
            'xml'
        )

        expected = 'eruditarticle/erudit:erudit.approchesind0522.approchesind01992.1032264ar.suffix.xml'

        self.assertEqual(expected, result)
